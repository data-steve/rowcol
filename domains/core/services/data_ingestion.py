from fastapi import HTTPException
from sqlalchemy.orm import Session
from domains.core.models.integration import Integration
from domains.core.models.transaction import Transaction
from domains.core.models.job import Job
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime

class DataIngestionService:
    def __init__(self, db: Session):
        self.db = db

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_platform_data(self, platform: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Fetch data from external platforms (QBO, Jobber, Stripe)."""
        if platform == "qbo":
            return self._fetch_qbo_data(credentials)
        elif platform == "jobber":
            return self._fetch_jobber_data(credentials)
        elif platform == "stripe":
            return self._fetch_stripe_data(credentials)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    def sync_qbo(self, firm_id: str, client_id: int, full_sync: bool = False) -> dict:
        """Legacy method - calls new fetch_platform_data for backward compatibility."""
        integration = self.db.query(Integration).filter_by(
            firm_id=firm_id, 
            platform="qbo"
        ).first()
        
        if not integration:
            return {"status": "error", "message": "QBO integration not found"}
            
        credentials = {"access_token": integration.access_token}
        return self._fetch_qbo_data(credentials)

    def _fetch_qbo_data(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Fetch QBO transactions, jobs, vendors."""
        integration = self.db.query(Integration).filter_by(platform="qbo").first()
        if not integration:
            raise HTTPException(status_code=404, detail="QBO integration not found")
            
        headers = {"Authorization": f"Bearer {integration.access_token}"}
        # TODO: Replace with real QBO API calls
        # Example: requests.get(f"{QBO_SANDBOX_URL}/{integration.account_id}/transactionlist", headers=headers)
        
        # Mock data for now
        transactions_data = [
            {"txn_id": f"QBO_{i}", "amount": 1000.00 + i, "date": "2025-08-01", "type": "deposit"} 
            for i in range(100)
        ]
        jobs_data = [
            {"job_id": f"JOB_{i}", "name": f"Job_{i}"} 
            for i in range(10)
        ]
        
        # Store in database
        for job_data in jobs_data:
            job = Job(
                job_id=job_data["job_id"],
                firm_id=integration.firm_id,
                client_id=integration.client_id,
                integration_id=integration.integration_id,
                platform_job_id=job_data["job_id"],
                name=job_data["name"],
                status="active"
            )
            self.db.merge(job)
            
        for txn_data in transactions_data:
            txn = Transaction(
                txn_id=txn_data["txn_id"],
                firm_id=integration.firm_id,
                client_id=integration.client_id,
                integration_id=integration.integration_id,
                platform_txn_id=txn_data["txn_id"],
                type=txn_data["type"],
                amount=txn_data["amount"],
                date=txn_data["date"],
                status="unmatched"
            )
            self.db.merge(txn)
            
        self.db.commit()
        return {"transactions": transactions_data, "jobs": jobs_data}

    def _fetch_jobber_data(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Fetch Jobber jobs and invoices via GraphQL API."""
        integration = self.db.query(Integration).filter_by(platform="jobber").first()
        if not integration:
            raise HTTPException(status_code=404, detail="Jobber integration not found")
            
        headers = {
            "Authorization": f"Bearer {integration.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Simple Jobber GraphQL queries for MVP
            jobs_query = """
            query GetJobs {
                jobs(first: 50, filter: { status: { in: [ACTIVE, IN_PROGRESS, SCHEDULED] } }) {
                    edges {
                        node {
                            id
                            title
                            status
                            startDate
                            endDate
                            customer { id name }
                            estimatedRevenue
                        }
                    }
                }
            }
            """
            
            invoices_query = """
            query GetInvoices {
                invoices(first: 100, filter: { status: { in: [SENT, PAID, OVERDUE] } }) {
                    edges {
                        node {
                            id
                            invoiceNumber
                            status
                            issueDate
                            paidDate
                            totalAmount
                            job { id title }
                        }
                    }
                }
            }
            """
            
            # Execute GraphQL queries
            jobber_api_url = "https://api.getjobber.com/api/graphql"
            
            jobs_response = requests.post(
                jobber_api_url,
                json={"query": jobs_query},
                headers=headers,
                timeout=30
            )
            jobs_response.raise_for_status()
            jobs_data = jobs_response.json()
            
            invoices_response = requests.post(
                jobber_api_url,
                json={"query": invoices_query},
                headers=headers,
                timeout=30
            )
            invoices_response.raise_for_status()
            invoices_data = invoices_response.json()
            
            # Parse and store data
            jobs = self._parse_jobber_jobs(jobs_data, integration)
            invoices = self._parse_jobber_invoices(invoices_data, integration)
            
            # Store in database
            for job_data in jobs:
                job = Job(
                    job_id=job_data["job_id"],
                    firm_id=integration.firm_id,
                    client_id=integration.client_id,
                    integration_id=integration.integration_id,
                    platform_job_id=job_data["platform_job_id"],
                    name=job_data["name"],
                    status=job_data["status"],
                    start_date=job_data.get("start_date"),
                    end_date=job_data.get("end_date")
                )
                self.db.merge(job)
            
            for txn_data in invoices:
                txn = Transaction(
                    txn_id=txn_data["txn_id"],
                    firm_id=integration.firm_id,
                    client_id=integration.client_id,
                    integration_id=integration.integration_id,
                    platform_txn_id=txn_data["platform_txn_id"],
                    type="invoice",
                    amount=txn_data["amount"],
                    date=txn_data["date"],
                    status="unmatched",
                    job_id=txn_data.get("job_id")
                )
                self.db.merge(txn)
            
            self.db.commit()
            return {"jobs": jobs, "invoices": invoices}
            
        except requests.exceptions.RequestException:
            # Fallback to simple mock data for development
            return self._generate_simple_jobber_mock_data(integration)
    
    def _parse_jobber_jobs(self, jobs_data: Dict, integration: Integration) -> List[Dict]:
        """Parse Jobber job data."""
        jobs = []
        
        if "data" in jobs_data and "jobs" in jobs_data["data"]:
            for edge in jobs_data["data"]["jobs"]["edges"]:
                job = edge["node"]
                
                start_date = self._parse_jobber_date(job.get("startDate"))
                end_date = self._parse_jobber_date(job.get("endDate"))
                
                jobs.append({
                    "job_id": f"JOB_{job['id']}",
                    "name": job.get("title", "Untitled Job"),
                    "platform_job_id": job["id"],
                    "status": job.get("status", "ACTIVE").lower(),
                    "start_date": start_date,
                    "end_date": end_date
                })
        
        return jobs
    
    def _parse_jobber_invoices(self, invoices_data: Dict, integration: Integration) -> List[Dict]:
        """Parse Jobber invoice data."""
        invoices = []
        
        if "data" in invoices_data and "invoices" in invoices_data["data"]:
            for edge in invoices_data["data"]["invoices"]["edges"]:
                invoice = edge["node"]
                
                issue_date = self._parse_jobber_date(invoice.get("issueDate"))
                paid_date = self._parse_jobber_date(invoice.get("paidDate"))
                total_amount = invoice.get("totalAmount", 0)
                
                invoices.append({
                    "txn_id": f"INV_{invoice['id']}",
                    "amount": total_amount,
                    "job_id": f"JOB_{invoice.get('job', {}).get('id', 'UNKNOWN')}",
                    "platform_txn_id": invoice["id"],
                    "type": "invoice",
                    "date": issue_date or "2025-01-01"
                })
        
        return invoices
    
    def _parse_jobber_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse Jobber date strings."""
        if not date_str:
            return None
        
        try:
            if "T" in date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d")
            else:
                return date_str
        except:
            return None
    
    def _generate_simple_jobber_mock_data(self, integration: Integration) -> Dict[str, Any]:
        """Prefer seeded DB data; fallback to minimal static preview."""
        try:
            # Prefer real rows if present
            db_jobs = (
                self.db.query(Job)
                .filter(Job.firm_id == integration.firm_id)
                .limit(10)
                .all()
            )
            db_invoices = (
                self.db.query(Transaction)
                .filter(
                    Transaction.firm_id == integration.firm_id,
                    Transaction.type == "invoice",
                )
                .limit(50)
                .all()
            )
            jobs = [
                {
                    "job_id": j.job_id,
                    "name": getattr(j, "name", j.job_id),
                    "platform_job_id": getattr(j, "platform_job_id", j.job_id),
                    "status": getattr(j, "status", "active"),
                    "start_date": getattr(j, "start_date", None),
                    "end_date": getattr(j, "end_date", None),
                }
                for j in db_jobs
            ]
            invoices = [
                {
                    "txn_id": t.txn_id,
                    "amount": t.amount,
                    "job_id": getattr(t, "job_id", None),
                    "platform_txn_id": t.platform_txn_id,
                    "type": t.type,
                    "date": t.date,
                }
                for t in db_invoices
            ]
            if jobs or invoices:
                return {"jobs": jobs, "invoices": invoices}
        except Exception:
            pass
        # Static minimal preview as last resort
        jobs = [
            {"job_id": f"JOB_{i}", "name": f"Job {i}", "platform_job_id": f"jobber_job_{i}", "status": "active"}
            for i in range(5)
        ]
        invoices = [
            {"txn_id": f"INV_{i}", "amount": 1000.00 + i * 100, "job_id": f"JOB_{i%5}", "platform_txn_id": f"jobber_inv_{i}", "type": "invoice", "date": "2025-01-15"}
            for i in range(10)
        ]
        return {"jobs": jobs, "invoices": invoices}

    def _fetch_stripe_data(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Fetch Stripe charges and payouts via REST API."""
        integration = self.db.query(Integration).filter_by(platform="stripe").first()
        if not integration:
            raise HTTPException(status_code=404, detail="Stripe integration not found")
            
        headers = {"Authorization": f"Bearer {integration.access_token}"}
        
        try:
            # Get Stripe charges
            charges_response = requests.get(
                "https://api.stripe.com/v1/charges",
                headers=headers,
                params={"limit": 100},
                timeout=30
            )
            charges_response.raise_for_status()
            charges_data = charges_response.json()
            
            # Get Stripe payouts
            payouts_response = requests.get(
                "https://api.stripe.com/v1/payouts", 
                headers=headers,
                params={"limit": 50},
                timeout=30
            )
            payouts_response.raise_for_status()
            payouts_data = payouts_response.json()
            
            # Parse and store data
            charges = self._parse_stripe_charges(charges_data, integration)
            payouts = self._parse_stripe_payouts(payouts_data, integration)
            
            # Store in database
            for txn_data in charges + payouts:
                txn = Transaction(
                    txn_id=txn_data["txn_id"],
                    firm_id=integration.firm_id,
                    client_id=integration.client_id,
                    integration_id=integration.integration_id,
                    platform_txn_id=txn_data["platform_txn_id"],
                    type=txn_data["type"],
                    amount=txn_data["amount"],
                    date=txn_data["date"],
                    status="unmatched"
                )
                self.db.merge(txn)
            
            self.db.commit()
            return {"charges": charges, "payouts": payouts}
            
        except requests.exceptions.RequestException:
            # Fallback to simple mock data for development
            return self._generate_simple_stripe_mock_data(integration)
    
    def _parse_stripe_charges(self, charges_data: Dict, integration: Integration) -> List[Dict]:
        """Parse Stripe charge data."""
        charges = []
        
        for charge in charges_data.get("data", []):
            charges.append({
                "txn_id": f"CHG_{charge['id']}",
                "amount": charge["amount"] / 100,  # Convert from cents
                "platform_txn_id": charge["id"],
                "type": "charge",
                "date": datetime.fromtimestamp(charge["created"]).strftime("%Y-%m-%d")
            })
        
        return charges
    
    def _parse_stripe_payouts(self, payouts_data: Dict, integration: Integration) -> List[Dict]:
        """Parse Stripe payout data."""
        payouts = []
        
        for payout in payouts_data.get("data", []):
            payouts.append({
                "txn_id": f"POUT_{payout['id']}",
                "amount": payout["amount"] / 100,  # Convert from cents
                "platform_txn_id": payout["id"],
                "type": "payout",
                "date": datetime.fromtimestamp(payout["created"]).strftime("%Y-%m-%d")
            })
        
        return payouts
    
    def _generate_simple_stripe_mock_data(self, integration: Integration) -> Dict[str, Any]:
        """Prefer seeded DB data; fallback to minimal static preview."""
        try:
            db_charges = (
                self.db.query(Transaction)
                .filter(Transaction.firm_id == integration.firm_id, Transaction.type == "charge")
                .limit(50)
                .all()
            )
            db_payouts = (
                self.db.query(Transaction)
                .filter(Transaction.firm_id == integration.firm_id, Transaction.type == "payout")
                .limit(20)
                .all()
            )
            charges = [
                {
                    "txn_id": t.txn_id,
                    "amount": t.amount,
                    "platform_txn_id": t.platform_txn_id,
                    "type": t.type,
                    "date": t.date,
                }
                for t in db_charges
            ]
            payouts = [
                {
                    "txn_id": t.txn_id,
                    "amount": t.amount,
                    "platform_txn_id": t.platform_txn_id,
                    "type": t.type,
                    "date": t.date,
                }
                for t in db_payouts
            ]
            if charges or payouts:
                return {"charges": charges, "payouts": payouts}
        except Exception:
            pass
        charges = [
            {"txn_id": f"CHG_{i}", "amount": 100.00 + i * 10, "platform_txn_id": f"stripe_charge_{i}", "type": "charge", "date": "2025-01-15"}
            for i in range(20)
        ]
        payouts = [
            {"txn_id": f"POUT_{i}", "amount": 500.00 + i * 50, "platform_txn_id": f"stripe_payout_{i}", "type": "payout", "date": "2025-01-15"}
            for i in range(5)
        ]
        return {"charges": charges, "payouts": payouts}
