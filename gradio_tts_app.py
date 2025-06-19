import random
from pathlib import Path

import numpy as np
import torch
import gradio as gr
from chatterbox.tts import ChatterboxTTS

LOCAL_JS = """
function loadItem(key){
  try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch(e){ return []; }
}
function saveItem(key,val){ localStorage.setItem(key, JSON.stringify(val)); }
function clearLS(){ localStorage.clear(); }
"""

EXAMPLE_TEXTS = [
    "Harambe was a great ape.",
    "Hello there! I'm the open source Chatterbox TTS from Resemble AI."
]


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def set_seed(seed: int):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)


def load_model():
    model = ChatterboxTTS.from_pretrained(DEVICE)
    return model


def generate(model, text, audio_prompt_path, exaggeration, temperature, seed_num, cfgw, min_p, top_p, repetition_penalty):
    if model is None:
        model = ChatterboxTTS.from_pretrained(DEVICE)

    if seed_num != 0:
        set_seed(int(seed_num))

    wav = model.generate(
        text,
        audio_prompt_path=audio_prompt_path,
        exaggeration=exaggeration,
        temperature=temperature,
        cfg_weight=cfgw,
        min_p=min_p,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
    )
    return (model.sr, wav.squeeze(0).numpy())


def add_prompt(queue, text):
    queue = queue or []
    if text:
        queue.append(text)
    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(queue))
    return queue, numbered


def add_sample(sample_list, sample_path):
    sample_list = sample_list or []
    if sample_path:
        sample_list.append(sample_path)
    names = [Path(p).name for p in sample_list]
    return sample_list, gr.Dropdown.update(choices=names, value=names[-1] if names else None)


def refresh_samples(sample_list):
    names = [Path(p).name for p in sample_list or []]
    return gr.Dropdown.update(choices=names, value=names[-1] if names else None)


def refresh_queue(queue):
    queue = queue or []
    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(queue))
    return numbered


def generate_next(model, queue, samples, selected_sample, text, exaggeration, temperature, seed_num, cfgw, min_p, top_p, repetition_penalty):
    if queue:
        prompt = queue.pop(0)
    else:
        prompt = text

    sample_path = None
    if selected_sample:
        for p in samples or []:
            if Path(p).name == selected_sample:
                sample_path = p
                break

    sr, wav = generate(
        model,
        prompt,
        sample_path,
        exaggeration,
        temperature,
        seed_num,
        cfgw,
        min_p,
        top_p,
        repetition_penalty,
    )

    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(queue))
    return (sr, wav), queue, numbered


def generate_all(model, queue, samples, selected_sample, text, exaggeration, temperature, seed_num, cfgw, min_p, top_p, repetition_penalty, keep_generating=False):
    result = None
    iterations = 0
    while queue:
        result, queue, _ = generate_next(
            model,
            queue,
            samples,
            selected_sample,
            text,
            exaggeration,
            temperature,
            seed_num,
            cfgw,
            min_p,
            top_p,
            repetition_penalty,
        )
        iterations += 1
        if iterations > 20:
            break
    if keep_generating and text:
        queue.append(text)
    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(queue))
    return result, queue, numbered


def clear_storage():
    return [], [], [], "", gr.Dropdown.update(choices=[], value=None)


with gr.Blocks(title="Chatterbox TTS", js=LOCAL_JS) as demo:
    gr.Markdown("# Chatterbox TTS\nGenerate expressive speech with your own voice sample.")
    model_state = gr.State(None)
    queue_state = gr.State([])
    sample_state = gr.State([])
    output_state = gr.State([])

    with gr.Tab("Synthesize"):
        with gr.Row():
            with gr.Column():
                text = gr.Textbox(
                    label="Text to synthesize",
                    max_lines=5,
                    placeholder="Enter text here...",
                    value=EXAMPLE_TEXTS[0],
                )
                gr.Examples(EXAMPLE_TEXTS, inputs=text, label="Example prompts")
                add_prompt_btn = gr.Button("Add to Queue")
                queue_display = gr.Textbox(label="Prompt Queue", interactive=False)

                sample_input = gr.Audio(sources=["upload", "microphone"], type="filepath", label="Add Voice Sample", value=None)
                add_sample_btn = gr.Button("Add Sample")
                sample_select = gr.Dropdown(label="Voice Sample", choices=[]) 
                exaggeration = gr.Slider(0.25, 2, step=.05, label="Exaggeration (Neutral = 0.5)", value=.5)
                cfg_weight = gr.Slider(0.0, 1, step=.05, label="CFG/Pace", value=0.5)

                with gr.Accordion("Advanced", open=False):
                    seed_num = gr.Number(value=0, label="Random seed (0 for random)")
                    temp = gr.Slider(0.05, 5, step=.05, label="temperature", value=.8)
                    min_p = gr.Slider(0.00, 1.00, step=0.01, label="min_p", value=0.05)
                    top_p = gr.Slider(0.00, 1.00, step=0.01, label="top_p", value=1.00)
                    repetition_penalty = gr.Slider(1.00, 2.00, step=0.1, label="repetition_penalty", value=1.2)

                add_prompt_btn.click(add_prompt, [queue_state, text], [queue_state, queue_display]).then(
                    None, None, None, js="(q)=>saveItem('queue', q)"
                )
                add_sample_btn.click(add_sample, [sample_state, sample_input], [sample_state, sample_select]).then(
                    None, None, None, js="(s)=>saveItem('samples', s)"
                )

                run_btn = gr.Button("Generate", variant="primary")
                generate_all_btn = gr.Button("Generate All")
                keep_gen = gr.Checkbox(label="Keep generating")
                clear_btn = gr.Button("Clear LocalStorage")

            with gr.Column():
                audio_output = gr.Audio(label="Output Audio")

        demo.load(fn=load_model, inputs=[], outputs=model_state)
        demo.load(
            fn=None,
            inputs=[],
            outputs=[sample_state, output_state, queue_state],
            js="()=>[loadItem('samples'), loadItem('outputs'), loadItem('queue')]",
        )
        demo.load(
            fn=refresh_samples,
            inputs=[sample_state],
            outputs=sample_select,
        )
        demo.load(
            fn=refresh_queue,
            inputs=[queue_state],
            outputs=queue_display,
        )

        run_btn.click(
            fn=generate_next,
            inputs=[
                model_state,
                queue_state,
                sample_state,
                sample_select,
                text,
                exaggeration,
                temp,
                seed_num,
                cfg_weight,
                min_p,
                top_p,
                repetition_penalty,
            ],
            outputs=[audio_output, queue_state, queue_display],
        ).then(None, None, None, js="(a,q)=>{let o=loadItem('outputs');o.push(a);saveItem('outputs',o);saveItem('queue',q);}")

        generate_all_btn.click(
            fn=generate_all,
            inputs=[
                model_state,
                queue_state,
                sample_state,
                sample_select,
                text,
                exaggeration,
                temp,
                seed_num,
                cfg_weight,
                min_p,
                top_p,
                repetition_penalty,
                keep_gen,
            ],
            outputs=[audio_output, queue_state, queue_display],
        ).then(None, None, None, js="(a,q)=>{let o=loadItem('outputs');o.push(a);saveItem('outputs',o);saveItem('queue',q);}")

        clear_btn.click(
            fn=clear_storage,
            inputs=[],
            outputs=[sample_state, queue_state, output_state, queue_display, sample_select],
            js="clearLS"
        )

    with gr.Tab("About"):
        gr.Markdown(
            "Chatterbox is an open source TTS model by [Resemble AI](https://resemble.ai)."
        )

if __name__ == "__main__":
    demo.queue(
        max_size=50,
        default_concurrency_limit=1,
    ).launch(share=True)
