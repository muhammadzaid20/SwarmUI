import csv
import os
from dataclasses import dataclass
from typing import List, Sequence

import gradio as gr

from modules import script_callbacks


@dataclass(frozen=True)
class TagEntry:
    name: str
    category: str
    count: int


EXTENSION_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS_DIR = os.path.join(EXTENSION_ROOT, "tags")
PRIMARY_TAGS_FILE = os.path.join(TAGS_DIR, "danbooru_tags.csv")
SAMPLE_TAGS_FILE = os.path.join(TAGS_DIR, "sample_tags.csv")

CATEGORY_LABELS = {
    "": "All",
    "0": "General",
    "1": "Artist",
    "3": "Copyright",
    "4": "Character",
    "5": "Meta",
}


def _read_tags_from_csv(path: str) -> List[TagEntry]:
    tags: List[TagEntry] = []
    if not os.path.exists(path):
        return tags

    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = (row.get("tag") or row.get("name") or "").strip()
            if not name:
                continue
            category = (row.get("category") or row.get("type") or "0").strip()
            count_value = row.get("count") or row.get("post_count") or "0"
            try:
                count = int(float(count_value))
            except ValueError:
                count = 0
            tags.append(TagEntry(name=name, category=category, count=count))

    return tags


def load_tags() -> List[TagEntry]:
    tags = _read_tags_from_csv(PRIMARY_TAGS_FILE)
    if not tags:
        tags = _read_tags_from_csv(SAMPLE_TAGS_FILE)
    return sorted(tags, key=lambda entry: entry.count, reverse=True)


def filter_tags(tags: Sequence[TagEntry], query: str, category: str) -> List[TagEntry]:
    filtered = tags
    query_value = (query or "").strip().lower()
    if category:
        filtered = [tag for tag in filtered if tag.category == category]
    if query_value:
        filtered = [tag for tag in filtered if query_value in tag.name.lower()]
    return filtered


def format_tag_label(tag: TagEntry) -> str:
    label = CATEGORY_LABELS.get(tag.category, "Other")
    return f"{tag.name} ({label}, {tag.count})"


def build_tag_choices(tags: Sequence[TagEntry]) -> List[str]:
    return [format_tag_label(tag) for tag in tags]


def parse_tag_value(label: str) -> str:
    if not label:
        return ""
    return label.split(" (", 1)[0].strip()


def refresh_tags_state() -> List[TagEntry]:
    return load_tags()


def update_tag_dropdown(tags: List[TagEntry], query: str, category: str):
    filtered = filter_tags(tags, query, category)
    choices = build_tag_choices(filtered)
    value = choices[0] if choices else None
    return gr.Dropdown.update(choices=choices, value=value)


def append_tag(prompt: str, selected_label: str) -> str:
    selected_tag = parse_tag_value(selected_label)
    if not selected_tag:
        return prompt or ""

    prompt_value = (prompt or "").strip()
    if not prompt_value:
        return selected_tag

    if prompt_value.endswith(","):
        return f"{prompt_value} {selected_tag}"

    return f"{prompt_value}, {selected_tag}"


def build_prompt_builder_ui():
    tags_state = gr.State(load_tags())

    with gr.Blocks() as prompt_builder_ui:
        gr.Markdown(
            """
            # Prompt Builder (Forge)
            Click tags to build a prompt. To use a full Danbooru tag list, place a CSV at
            `extensions/PromptBuilder/tags/danbooru_tags.csv` with headers like `tag,category,count`.
            """
        )

        prompt = gr.Textbox(
            label="Prompt",
            elem_id="prompt_builder_prompt",
            lines=3,
            placeholder="Click tags to build your prompt...",
        )

        with gr.Row():
            search = gr.Textbox(label="Search", placeholder="e.g. cyberpunk")
            category = gr.Dropdown(
                label="Category",
                choices=[(label, key) for key, label in CATEGORY_LABELS.items()],
                value="",
            )

        with gr.Row():
            tag_dropdown = gr.Dropdown(label="Tags", choices=build_tag_choices(tags_state.value))
            add_tag = gr.Button("Add tag")

        with gr.Row():
            refresh = gr.Button("Reload tag list")

        gr.HTML(
            """
            <div class="prompt-builder-actions">
              <button class="gr-button" onclick="promptBuilderSend('txt2img_prompt')">Send to txt2img</button>
              <button class="gr-button" onclick="promptBuilderSend('img2img_prompt')">Send to img2img</button>
            </div>
            """
        )

        add_tag.click(append_tag, inputs=[prompt, tag_dropdown], outputs=prompt)

        search.change(update_tag_dropdown, inputs=[tags_state, search, category], outputs=tag_dropdown)
        category.change(update_tag_dropdown, inputs=[tags_state, search, category], outputs=tag_dropdown)

        refresh.click(refresh_tags_state, outputs=tags_state).then(
            update_tag_dropdown, inputs=[tags_state, search, category], outputs=tag_dropdown
        )

    return prompt_builder_ui, "Prompt Builder", "prompt_builder_tab"


def on_ui_tabs():
    return [build_prompt_builder_ui()]


script_callbacks.on_ui_tabs(on_ui_tabs)
