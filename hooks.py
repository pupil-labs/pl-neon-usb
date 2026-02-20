import os

from mkdocs.structure.files import File


def on_files(files, config):
    example_dir = "examples"
    docs_dir = config["docs_dir"]

    if not os.path.exists(example_dir):
        return files

    # We will store our new pages here to add them to the nav later
    generated_pages = []

    for filename in sorted(os.listdir(example_dir)):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            # Create a path relative to the docs folder
            # e.g., 'generated_examples/imu.md'
            md_rel_path = f"generated_examples/{module_name}.md"
            full_md_path = os.path.join(docs_dir, md_rel_path)

            os.makedirs(os.path.dirname(full_md_path), exist_ok=True)

            # Read Python code and wrap in Markdown
            with open(os.path.join(example_dir, filename), encoding="utf-8") as f:
                code_content = f.read()

            title = module_name.replace("_", " ").title()
            with open(full_md_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n```python\n{code_content}\n```")

            # Register file with MkDocs
            new_file = File(
                path=md_rel_path,
                src_dir=docs_dir,
                dest_dir=config["site_dir"],
                use_directory_urls=config["use_directory_urls"],
            )
            files.append(new_file)

            # Save the title and path for the nav
            generated_pages.append({title: md_rel_path})

    # Update the Navigation dynamically
    for item in config["nav"]:
        if isinstance(item, dict) and "Examples" in item:
            item["Examples"] = generated_pages

    return files
