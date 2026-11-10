for (const button of document.querySelectorAll('[data-copy]')) {
  const original = button.textContent;
  button.addEventListener('click', async () => {
    const text = button.dataset.copy;
    let copied = false;
    if (navigator.clipboard?.writeText) {
      try { await navigator.clipboard.writeText(text); copied = true; } catch {}
    }
    if (!copied) {
      const field = document.createElement('textarea');
      field.value = text;
      field.setAttribute('readonly', '');
      field.style.position = 'fixed';
      field.style.opacity = '0';
      document.body.append(field);
      field.select();
      try { copied = document.execCommand('copy'); } catch {}
      field.remove();
      button.focus();
    }
    button.textContent = copied ? '已复制' : '请手动复制';
    document.getElementById('copy-status').textContent = copied ? '命令已复制到剪贴板' : '无法访问剪贴板，请手动复制命令';
    clearTimeout(button.restoreTimer);
    button.restoreTimer = setTimeout(() => { button.textContent = original; }, 2200);
  });
}
