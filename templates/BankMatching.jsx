```jsx
/**
 * BankMatching.jsx: React/Tailwind CSS component for Stage 1C of the Escher project.
 * Review queue for bank transactions with 0.6-0.89 confidence scores.
 * Three-pane UX: lanes (left), transaction details (center), actions (right).
 * Dependencies: /api/bank/transactions, /api/bank/transactions/categorize.
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BankMatching = ({ firmId, clientId }) => {
  const [transactions, setTransactions] = useState([]);
  const [selectedTxn, setSelectedTxn] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch transactions with 0.6-0.89 confidence
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/bank/transactions', {
          params: { firm_id: firmId, client_id: clientId },
        });
        // Filter for 0.6-0.89 confidence
        const filteredTxns = response.data.filter(
          (txn) => txn.confidence >= 0.6 && txn.confidence <= 0.89
        );
        setTransactions(filteredTxns);
        setSelectedTxn(filteredTxns[0] || null);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch transactions');
        setLoading(false);
      }
    };
    fetchTransactions();
  }, [firmId, clientId]);

  // Handle action (Accept, Recur, Exception)
  const handleAction = async (action, transactionId) => {
    try {
      if (action === 'accept' || action === 'recur') {
        await axios.post('/api/bank/transactions/categorize', {
          transaction_id: transactionId,
          description: selectedTxn.description,
          amount: selectedTxn.amount,
        }, { params: { firm_id: firmId } });
      } else if (action === 'exception') {
        // Redirect to document_review.html (assumed route)
        window.location.href = `/document_review?txn_id=${transactionId}`;
      }
      // Refresh transactions
      const response = await axios.get('/api/bank/transactions', {
        params: { firm_id: firmId, client_id: clientId },
      });
      const filteredTxns = response.data.filter(
        (txn) => txn.confidence >= 0.6 && txn.confidence <= 0.89
      );
      setTransactions(filteredTxns);
      setSelectedTxn(filteredTxns[0] || null);
    } catch (err) {
      setError(`Failed to process ${action}`);
    }
  };

  // Categorize transactions into lanes
  const highDollarTxns = transactions.filter((txn) => txn.amount > 10000);
  const newVendorTxns = transactions.filter((txn) =>
    txn.description.toLowerCase().includes('new vendor')
  );
  const unreconciledTxns = transactions.filter((txn) => txn.status === 'pending');

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Pane: Lanes */}
      <div className="w-1/4 p-4 bg-white border-r">
        <h2 className="text-lg font-bold mb-4">Transaction Lanes</h2>
        <div className="mb-4">
          <h3 className="font-semibold">High $</h3>
          <ul>
            {highDollarTxns.map((txn) => (
              <li
                key={txn.transaction_id}
                className={`p-2 cursor-pointer ${selectedTxn?.transaction_id === txn.transaction_id ? 'bg-blue-100' : ''}`}
                onClick={() => setSelectedTxn(txn)}
              >
                {txn.description} (${txn.amount})
              </li>
            ))}
          </ul>
        </div>
        <div className="mb-4">
          <h3 className="font-semibold">New Vendor</h3>
          <ul>
            {newVendorTxns.map((txn) => (
              <li
                key={txn.transaction_id}
                className={`p-2 cursor-pointer ${selectedTxn?.transaction_id === txn.transaction_id ? 'bg-blue-100' : ''}`}
                onClick={() => setSelectedTxn(txn)}
              >
                {txn.description}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-semibold">Unreconciled</h3>
          <ul>
            {unreconciledTxns.map((txn) => (
              <li
                key={txn.transaction_id}
                className={`p-2 cursor-pointer ${selectedTxn?.transaction_id === txn.transaction_id ? 'bg-blue-100' : ''}`}
                onClick={() => setSelectedTxn(txn)}
              >
                {txn.description}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Center Pane: Transaction Details */}
      <div className="w-1/2 p-4 bg-white">
        <h2 className="text-lg font-bold mb-4">Transaction Details</h2>
        {selectedTxn ? (
          <div>
            <p><strong>Memo:</strong> {selectedTxn.description}</p>
            <p><strong>Vendor:</strong> {selectedTxn.vendor_name || 'Unknown'}</p>
            <p><strong>Suggestion:</strong> {selectedTxn.account_id || 'None'}</p>
            <p><strong>Confidence:</strong> {selectedTxn.confidence}</p>
            <div className="mt-4">
              <strong>Document Preview:</strong>
              <a
                href={`/document_review?txn_id=${selectedTxn.transaction_id}`}
                className="text-blue-500 underline"
              >
                View Document
              </a>
            </div>
          </div>
        ) : (
          <p>No transaction selected</p>
        )}
      </div>

      {/* Right Pane: Actions */}
      <div className="w-1/4 p-4 bg-white border-l">
        <h2 className="text-lg font-bold mb-4">Actions</h2>
        {selectedTxn && (
          <div className="space-y-2">
            <button
              className="w-full bg-green-500 text-white p-2 rounded"
              onClick={() => handleAction('accept', selectedTxn.transaction_id)}
            >
              Accept (A)
            </button>
            <button
              className="w-full bg-blue-500 text-white p-2 rounded"
              onClick={() => handleAction('recur', selectedTxn.transaction_id)}
            >
              Recur (R)
            </button>
            <button
              className="w-full bg-red-500 text-white p-2 rounded"
              onClick={() => handleAction('exception', selectedTxn.transaction_id)}
            >
              Exception (X)
            </button>
          </div>
        )}
        {/* Binder Status Widget */}
        <div className="mt-4">
          <h3 className="font-semibold">Binder Status</h3>
          <p>Pending: {transactions.length} transactions</p>
        </div>
      </div>

      {/* Loading/Error States */}
      {loading && <div className="absolute inset-0 flex items-center justify-center">Loading...</div>}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center text-red-500">
          {error}
        </div>
      )}
    </div>
  );
};

export default BankMatching;
```

#### Stage 1D: `payroll_review.html` (as `PayrollReview.jsx`)
<xaiArtifact artifact_id="cc5513cc-dbd7-472a-9f02-3f3614d72ae5" artifact_version_id="3f5507bf-924c-43c8-9d62-c2a0aaab0d45" title="PayrollReview.jsx" contentType="text/jsx">
```jsx
/**
 * PayrollReview.jsx: React/Tailwind CSS component for Stage 1D of the Escher project.
 * Cockpit for GL posting of payroll batches.
 * Three-pane UX: batch list (left), batch details (center), actions (right).
 * Dependencies: /api/payroll/batches, /api/payroll/reconcile/{batch_id}.
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PayrollReview = ({ firmId, clientId }) => {
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch payroll batches
  useEffect(() => {
    const fetchBatches = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/payroll/batches', {
          params: { firm_id: firmId, client_id: clientId },
        });
        setBatches(response.data);
        setSelectedBatch(response.data[0] || null);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch payroll batches');
        setLoading(false);
      }
    };
    fetchBatches();
  }, [firmId, clientId]);

  // Handle action (Approve, Reject, Reconcile)
  const handleAction = async (action, batchId) => {
    try {
      if (action === 'reconcile') {
        const response = await axios.post(`/api/payroll/reconcile/${batchId}`, {}, {
          params: { firm_id: firmId },
        });
        setBatches(batches.map((b) =>
          b.batch_id === batchId ? response.data : b
        ));
        setSelectedBatch(response.data);
      } else if (action === 'approve' || action === 'reject') {
        // Placeholder for approve/reject logic (not specified in plan)
        alert(`${action} action not implemented`);
      }
    } catch (err) {
      setError(`Failed to process ${action}`);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Pane: Batch List */}
      <div className="w-1/4 p-4 bg-white border-r">
        <h2 className="text-lg font-bold mb-4">Payroll Batches</h2>
        <ul>
          {batches.map((batch) => (
            <li
              key={batch.batch_id}
              className={`p-2 cursor-pointer ${selectedBatch?.batch_id === batch.batch_id ? 'bg-blue-100' : ''}`}
              onClick={() => setSelectedBatch(batch)}
            >
              {batch.description || `Batch ${batch.batch_id}`} (${batch.total_amount})
            </li>
          ))}
        </ul>
      </div>

      {/* Center Pane: Batch Details */}
      <div className="w-1/2 p-4 bg-white">
        <h2 className="text-lg font-bold mb-4">Batch Details</h2>
        {selectedBatch ? (
          <div>
            <p><strong>Batch ID:</strong> {selectedBatch.batch_id}</p>
            <p><strong>Total Amount:</strong> ${selectedBatch.total_amount}</p>
            <p><strong>Payroll Date:</strong> {new Date(selectedBatch.payroll_date).toLocaleDateString()}</p>
            <p><strong>Period:</strong> {new Date(selectedBatch.period_start).toLocaleDateString()} - {new Date(selectedBatch.period_end).toLocaleDateString()}</p>
            <p><strong>Status:</strong> {selectedBatch.status}</p>
            <div className="mt-4">
              <strong>Journal Entry:</strong>
              <pre className="bg-gray-200 p-2 rounded">
                {JSON.stringify({
                  account: '6090-Payroll Services',
                  amount: selectedBatch.total_amount,
                  date: selectedBatch.payroll_date,
                }, null, 2)}
              </pre>
            </div>
            <div className="mt-4">
              <strong>Document Preview:</strong>
              <a
                href={`/document_review?batch_id=${selectedBatch.batch_id}`}
                className="text-blue-500 underline"
              >
                View Document
              </a>
            </div>
          </div>
        ) : (
          <p>No batch selected</p>
        )}
      </div>

      {/* Right Pane: Actions */}
      <div className="w-1/4 p-4 bg-white border-l">
        <h2 className="text-lg font-bold mb-4">Actions</h2>
        {selectedBatch && (
          <div className="space-y-2">
            <button
              className="w-full bg-green-500 text-white p-2 rounded"
              onClick={() => handleAction('approve', selectedBatch.batch_id)}
            >
              Approve
            </button>
            <button
              className="w-full bg-red-500 text-white p-2 rounded"
              onClick={() => handleAction('reject', selectedBatch.batch_id)}
            >
              Reject
            </button>
            <button
              className="w-full bg-blue-500 text-white p-2 rounded"
              onClick={() => handleAction('reconcile', selectedBatch.batch_id)}
            >
              Reconcile
            </button>
          </div>
        )}
      </div>

      {/* Loading/Error States */}
      {loading && <div className="absolute inset-0 flex items-center justify-center">Loading...</div>}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center text-red-500">
          {error}
        </div>
      )}
    </div>
  );
};

export default PayrollReview;
```

### Notes on Implementation
- **BankMatching.jsx (Stage 1C)**:
  - **Three-Pane UX**:
    - **Left**: Displays transactions in three lanes (High $, New Vendor, Unreconciled) based on amount (> $10,000), description (contains “new vendor”), and status (`pending`).
    - **Center**: Shows details of the selected transaction (memo, vendor, suggestion, confidence) with a link to `document_review.html`.
    - **Right**: Provides buttons for Accept, Recur, and Exception actions, calling `/api/bank/transactions/categorize` for Accept/Recur and redirecting to `document_review.html` for Exception.
  - **Features**: Binder status widget shows the number of pending transactions.
  - **API Integration**: Fetches transactions from `/api/bank/transactions` with `firm_id` and `client_id` parameters, filtering for 0.6-0.89 confidence scores.
  - **Guidelines**: Uses basic React with Tailwind CSS, Axios for API calls (tested lightweight library), and raw JavaScript for action handling. Avoids Jinja2 conflicts and heavy libraries.

- **PayrollReview.jsx (Stage 1D)**:
  - **Three-Pane UX**:
    - **Left**: Lists payroll batches with description and total amount.
    - **Center**: Displays batch details (ID, amount, payroll date, period, status, journal entry) with a link to `document_review.html`.
    - **Right**: Provides Approve, Reject, and Reconcile buttons, with Reconcile calling `/api/payroll/reconcile/{batch_id}`. Approve/Reject are placeholders (not specified in plan).
  - **API Integration**: Fetches batches from `/api/payroll/batches` and reconciles via `/api/payroll/reconcile/{batch_id}` with `firm_id` parameter.
  - **Guidelines**: Uses basic React with Tailwind CSS, Axios for API calls, and raw JavaScript. Avoids heavy libraries and Jinja2 conflicts.

- **Assumptions**:
  - `firmId` and `clientId` are passed as props (e.g., from a parent component or route).
  - `document_review.html` is a placeholder route; actual implementation would require its definition.
  - Approve/Reject actions in `PayrollReview.jsx` are placeholders, as the dev plan didn’t specify their behavior.

- **Integration**:
  - Ensure Axios is included in the project (e.g., via `npm install axios`).
  - Add these components to your React app’s router (e.g., in `src/App.js`):
    ```jsx
    import { BrowserRouter, Route, Routes } from 'react-router-dom';
    import BankMatching from './components/BankMatching';
    import PayrollReview from './components/PayrollReview';

    function App() {
      return (
        <BrowserRouter>
          <Routes>
            <Route path="/bank_matching" element={<BankMatching firmId="550e8400-e29b-41d4-a716-446655440000" clientId={1} />} />
            <Route path="/payroll_review" element={<PayrollReview firmId="550e8400-e29b-41d4-a716-446655440000" clientId={1} />} />
          </Routes>
        </BrowserRouter>
      );
    }
    ```
  - Ensure `routes/payroll.py` and `routes/bank.py` are registered in `main.py` (as noted in previous artifacts).

### Next Steps
1. **Validation**: Please review `BankMatching.jsx` and `PayrollReview.jsx` to confirm they meet the three-pane UX requirements and integrate with the backend APIs. Test with the provided `firm_id` and `client_id` from `seed_data.sql`.
2. **Testing**: Add frontend tests (e.g., using Jest/React Testing Library) to verify rendering, API calls, and action handling. I can provide test files if needed.
3. **Feedback**: Let me know if additional UI features (e.g., specific Approve/Reject logic, styling tweaks) or `document_review.html` are required.
4. **Next Stage**: Confirm if Stage 1D is complete or if further refinements (e.g., additional templates, backend tweaks) are needed. Specify the next stage (e.g., Stage 1E) if ready.

Sorry again for misinterpreting "templates" as seed data. Does this cover the UI needs for Stages 1C and 1D? Let me know how to proceed!