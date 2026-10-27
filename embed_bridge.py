"""Content-height only: no form values, services, or Streamlit DOM internals."""
import re
import streamlit as st

_bridge = st.components.v2.component(
    "contract_content_height",
    html='<div class="contract-end" aria-hidden="true"></div>',
    css='.contract-end { height: 1px; pointer-events: none; }',
    js="""
    export default function({ parentElement, data }) {
        const marker = parentElement.querySelector('.contract-end');
        let frame = 0, last = 0;
        const measure = () => {
            frame = 0;
            const height = Math.ceil(marker.getBoundingClientRect().bottom + window.scrollY + 64);
            if (height >= 400 && height <= 12000 && Math.abs(height - last) > 2) {
                last = height;
                window.top.postMessage({ type: 'contract:height', id: data.id, height }, data.origin);
            }
        };
        const schedule = () => { if (!frame) frame = requestAnimationFrame(measure); };
        const mutations = new MutationObserver(schedule);
        mutations.observe(document.body, { childList: true, subtree: true, characterData: true });
        const sizes = new ResizeObserver(schedule);
        sizes.observe(document.documentElement);
        window.addEventListener('resize', schedule);
        document.fonts.ready.then(schedule);
        schedule();
        return () => {
            mutations.disconnect(); sizes.disconnect();
            window.removeEventListener('resize', schedule);
            cancelAnimationFrame(frame);
        };
    }
    """,
)


def render_embed_bridge():
    if not st.context.is_embedded:
        return
    instance = st.query_params.get("embed_id", "")
    origin = st.query_params.get("host_origin", "")
    allowed = origin == "https://daniel-w-portfolio.vercel.app" or re.fullmatch(
        r"http://(?:127[.]0[.]0[.]1|localhost)(?::[1-9][0-9]{0,4})?", origin
    )
    if allowed and re.fullmatch(r"[a-f0-9-]{32,36}", instance):
        _bridge(data={"id": instance, "origin": origin}, key="contract_height")
