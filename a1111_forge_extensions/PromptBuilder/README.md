# Prompt Builder (A1111/Forge)

This is a Forge-compatible port of the SwarmUI Prompt Builder extension. It adds a **Prompt Builder** tab that lets you browse Danbooru-style tags and build prompts by clicking them.

## Usage

1. Copy this folder into your Forge `extensions/` directory (for example `stable-diffusion-webui-forge/extensions/PromptBuilder`).
2. (Optional) Provide a tag list CSV at `extensions/PromptBuilder/tags/danbooru_tags.csv` with headers like `tag,category,count`.
3. Launch Forge and open the **Prompt Builder** tab.
4. Click **Add tag** to append the selected tag to the prompt, then use **Send to txt2img** or **Send to img2img** to copy the prompt into the main UI.

## Tag CSV format

The CSV reader supports headers:

- `tag` or `name`
- `category` or `type` (0=General, 1=Artist, 3=Copyright, 4=Character, 5=Meta)
- `count` or `post_count`

A tiny sample file is included at `tags/sample_tags.csv` and is used automatically if no main tag list exists.

## Credits

Original SwarmUI extension by Juan Treminio: <https://github.com/jtreminio/SwarmUI-PromptBuilderExtension>
