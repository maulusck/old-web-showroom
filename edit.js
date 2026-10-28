// edit.js — opt-in content editor. Open any template with ?edit to switch on.
// Makes every [data-slot] editable; "Save" downloads the edited HTML to replace the file.
// ponytail: text-only, native contenteditable + Blob download. No lib, no storage, no server.
if (location.search.includes('edit')) addEventListener('DOMContentLoaded', () => {
  const slots = document.querySelectorAll('[data-slot]');
  slots.forEach(el => { el.contentEditable = 'true'; el.style.outline = '1px dashed rgba(128,128,128,.7)'; });
  const b = document.createElement('button');
  b.textContent = '💾 Save HTML';
  b.style.cssText = 'position:fixed;bottom:10px;right:10px;z-index:99999;padding:8px 12px;font:13px monospace;cursor:pointer';
  b.onclick = () => {
    slots.forEach(el => { el.removeAttribute('contenteditable'); el.style.outline = ''; });
    b.remove();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['<!DOCTYPE html>\n' + document.documentElement.outerHTML], { type: 'text/html' }));
    a.download = location.pathname.split('/').pop() || 'page.html';
    a.click();
    location.reload();
  };
  document.body.append(b);
});
