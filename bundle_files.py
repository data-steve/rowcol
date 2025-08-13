# bundle_files.py
#
# Example usage:
# python bundle_files.py --modules fixed_assets core \
#   --entities engagement asset \
#   --folders app/data/lookups/asset_classification \
#   --files app/data/tax_rules/tax_rules_2025.json \
#   --output bundle.json

import argparse
import json
import os
import logging
from pathlib import Path
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_matching_files(glob_pattern, project_root):
    return glob.glob(os.path.join(project_root, glob_pattern), recursive=True)

def get_entity_files(entity: str, project_root: str) -> list[dict]:
    entity = entity.lower()
    entity_files = []

    search_paths = [
        f"app/core/models/{entity}.py",
        f"app/modules/*/models/{entity}.py",
        f"app/core/services/{entity}.py",
        f"app/modules/*/services/{entity}.py",
    ]

    for pattern in search_paths:
        matches = find_matching_files(pattern, project_root)
        if not matches:
            continue
        for match in matches:
            if "__pycache__" in match or not os.path.isfile(match):
                continue
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
            break  # Stop after first match per pattern

    return entity_files

def get_module_files(module: str, project_root: str) -> list[dict]:
    module = module.lower()
    module_files = []
    base_path = "app/core" if module == "core" else f"app/modules/{module}"
    paths = {
        "models": f"{base_path}/models/*.py",
        "services": f"{base_path}/services/*.py",
    }

    for label, pattern in paths.items():
        matches = find_matching_files(pattern, project_root)
        for match in matches:
            if os.path.isfile(match) and "__pycache__" not in match:
                try:
                    with open(match, "r", encoding="utf-8") as f:
                        content = f.read()
                    rel_path = os.path.relpath(match, project_root)
                    module_files.append({
                        "filename": os.path.basename(match),
                        "path": rel_path,
                        "content": content,
                        "module": module.capitalize(),
                        "category": label
                    })
                    logger.info(f"Added {rel_path} for module {module}, category {label}")
                except Exception as e:
                    logger.warning(f"Failed to read {match}: {e}")
    return module_files

def get_folder_files(folder: str, project_root: str) -> list[dict]:
    folder_files = []
    folder_path = os.path.join(project_root, folder.replace("/", os.sep))

    if os.path.isdir(folder_path):
        for root, _, files in os.walk(folder_path):
            if "__pycache__" in root:
                continue
            for file in files:
                if file.endswith((".py", ".json", ".md")):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        rel_path = os.path.relpath(full_path, project_root)
                        folder_files.append({
                            "filename": file,
                            "path": rel_path,
                            "content": content,
                            "module": None,
                            "category": "data" if file.endswith(".json") else "docs"
                        })
                        logger.info(f"Added {rel_path} from folder {folder}")
                    except Exception as e:
                        logger.warning(f"Failed to read {full_path}: {e}")
    elif os.path.isfile(folder_path) and folder_path.endswith((".py", ".json", ".md")):
        try:
            with open(folder_path, "r", encoding="utf-8") as f:
                content = f.read()
            rel_path = os.path.relpath(folder_path, project_root)
            folder_files.append({
                "filename": os.path.basename(folder_path),
                "path": rel_path,
                "content": content,
                "module": None,
                "category": "data" if folder_path.endswith(".json") else "docs"
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
                    "module": None,
                    "category": "data" if file.endswith(".json") else "docs"
                })
                logger.info(f"Added standalone file {rel_path}")
            except Exception as e:
                logger.warning(f"Failed to read {full_path}: {e}")
        else:
            logger.warning(f"File {file} not found")
    return collected

def bundle_files(modules: list[str], folders: list[str], project_root: str, output: str, files: list[str], entities: list[str]):
    bundle = {
        "modules": {},
        "folders": {},
        "files": [],
        "entities": {}
    }

    for module in modules:
        bundle["modules"][module] = get_module_files(module, project_root)

    for folder in folders:
        bundle["folders"][folder] = get_folder_files(folder, project_root)

    for entity in entities:
        bundle["entities"][entity] = get_entity_files(entity, project_root)

    bundle["files"] = get_explicit_files(files, project_root)

    try:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)
        logger.info(f"Bundle written to {output}")
    except Exception as e:
        logger.error(f"Failed to write bundle to {output}: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Bundle project files by module, entity, folder, or specific files.")
    parser.add_argument("--entities", nargs="*", default=[], help="Entity names (e.g., asset, engagement, client)")
    parser.add_argument("--modules", nargs="*", default=[], help="Module names (e.g., core, fixed_assets)")
    parser.add_argument("--folders", nargs="*", default=[], help="Folders or shared files")
    parser.add_argument("--files", nargs="*", default=[], help="Specific file paths to include (e.g., JSON files)")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", default="bundle.json", help="Output JSON file")

    args = parser.parse_args()

    if not (args.modules or args.folders or args.files or args.entities):
        logger.warning("No modules, entities, folders, or files specified; creating an empty bundle")
        bundle_files([], [], args.project_root, args.output, [], [])
        return

    bundle_files(args.modules, args.folders, args.project_root, args.output, args.files, args.entities)

if __name__ == "__main__":
    main()