function promptBuilderFindTextarea(rootId) {
  if (!rootId) {
    return null;
  }
  const root = document.getElementById(rootId);
  if (!root) {
    return null;
  }
  if (root.tagName && root.tagName.toLowerCase() === 'textarea') {
    return root;
  }
  return root.querySelector('textarea');
}

function promptBuilderGetPrompt() {
  const promptField = promptBuilderFindTextarea('prompt_builder_prompt');
  return promptField ? promptField.value : '';
}

function promptBuilderSetPrompt(targetId, value) {
  const target = promptBuilderFindTextarea(targetId);
  if (!target) {
    return;
  }
  target.value = value;
  target.dispatchEvent(new Event('input', { bubbles: true }));
}

window.promptBuilderSend = function promptBuilderSend(targetId) {
  const value = promptBuilderGetPrompt();
  if (!value) {
    return;
  }
  promptBuilderSetPrompt(targetId, value);
};
