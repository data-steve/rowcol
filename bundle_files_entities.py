# bundle_files.py
#
# Example usage:
# python bundle_files.py --entities depreciation engagement \
#   --folders engine/hash engine/data/appendix_A/scripts \
#   --files engine/data/appendix_A/tables/columnar/a6.json engine/data/appendix_A/tables/processed/a6.json \
#           engine/data/appendix_A/tables/columnar/a4.json engine/data/appendix_A/tables/processed/a4.json \
#           engine/data/appendix_A/charts/processed/chart_1.json engine/data/appendix_A/charts/processed/chart_2.json \
#   --output bundle.json

import argparse
import json
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import glob

def find_matching_file(glob_pattern, project_root):
    matches = glob.glob(os.path.join(project_root, glob_pattern))
    return matches[0] if matches else None

def get_entity_files(entity: str, project_root: str) -> list[dict]:
    entity = entity.lower()
    entity_files = []
    paths = {
        "models": f"models/{entity}*.py",
        # "schemas": f"schemas/{entity}*.py",
        "services": f"services/{entity}*.py",
        # "routes": f"routes/{entity}*.py",
        # "tests": f"tests/test_{entity}*.py",
    }

    for label, pattern in paths.items():
        match = find_matching_file(pattern, project_root)
        if match and os.path.isfile(match):
            with open(match, "r", encoding="utf-8") as f:
                content = f.read()
            rel_path = os.path.relpath(match, project_root)
            entity_files.append({
                "filename": os.path.basename(match),
                "path": rel_path,
                "content": content,
                "entity": entity.capitalize()
            })
            logger.info(f"Added {rel_path} for entity {entity}")
    return entity_files


def get_folder_files(folder: str, project_root: str) -> list[dict]:
    folder_files = []
    folder_path = os.path.join(project_root, folder.replace("/", os.sep))

    if os.path.isdir(folder_path):
        for root, _, files in os.walk(folder_path):
            if "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        rel_path = os.path.relpath(full_path, project_root)
                        folder_files.append({
                            "filename": file,
                            "path": rel_path,
                            "content": content,
                            "entity": None
                        })
                        logger.info(f"Added {rel_path} from folder {folder}")
                    except Exception as e:
                        logger.warning(f"Failed to read {full_path}: {e}")
    elif os.path.isfile(folder_path) and folder_path.endswith(".py"):
        try:
            with open(folder_path, "r", encoding="utf-8") as f:
                content = f.read()
            rel_path = os.path.relpath(folder_path, project_root)
            folder_files.append({
                "filename": os.path.basename(folder_path),
                "path": rel_path,
                "content": content,
                "entity": None
            })
            logger.info(f"Added {rel_path} as shared file")
        except Exception as e:
            logger.warning(f"Failed to read {folder_path}: {e}")
    else:
        logger.warning(f"Folder or file {folder} not found")

    return folder_files

def get_explicit_files(files: list[str], project_root: str) -> list[dict]:
    collected = []
    for file in files:
        full_path = os.path.join(project_root, file)
        if os.path.isfile(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                rel_path = os.path.relpath(full_path, project_root)
                collected.append({
                    "filename": os.path.basename(full_path),
                    "path": rel_path,
                    "content": content,
                    "entity": None
                })
                logger.info(f"Added standalone file {rel_path}")
            except Exception as e:
                logger.warning(f"Failed to read {full_path}: {e}")
        else:
            logger.warning(f"File {file} not found")
    return collected

def bundle_files(entities: list[str], folders: list[str], project_root: str, output: str, files: list[str]):
    bundle = {"entities": {}, "folders": {}, "files": []}

    for entity in entities:
        bundle["entities"][entity] = get_entity_files(entity, project_root)

    for folder in folders:
        bundle["folders"][folder] = get_folder_files(folder, project_root)

    bundle["files"] = get_explicit_files(files, project_root)

    try:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)
        logger.info(f"Bundle written to {output}")
    except Exception as e:
        logger.error(f"Failed to write bundle to {output}: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Bundle project files by entity and folder.")
    parser.add_argument("--entities", nargs="*", default=[], help="Entity names (singular, e.g., user, firm)")
    parser.add_argument("--folders", nargs="*", default=[], help="Folders or shared files (e.g., core, dependencies.py)")
    parser.add_argument("--files", nargs="*", default=[], help="Specific file paths to include (e.g., JSON files)")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", default="bundle.json", help="Output JSON file")

    args = parser.parse_args()

    if not args.entities and not args.folders and not args.files:
        parser.error("At least one of --entities, --folders, or --files must be specified")

    bundle_files(args.entities, args.folders, args.project_root, args.output, args.files)

if __name__ == "__main__":
    main()
