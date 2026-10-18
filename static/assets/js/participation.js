(() => {
  const form = document.querySelector('[data-volunteer-form]');
  if (!form) return;
  const email = form.querySelector('[name="email"]');
  const phone = form.querySelector('[name="phone"]');
  const button = form.querySelector('[type="submit"]');
  const label = button?.querySelector('[data-submit-label]');
  const status = form.querySelector('[data-offer-status]');
  const interest = form.querySelector('[name="interest"]');
  const context = form.querySelector('[data-offer-context]');
  const descriptions = {
    GUEST_CLASS: 'Share a subject you know. The team can help plan a guest class with the school.',
    SEMINAR: 'Share a useful perspective through a career talk, seminar, or practical workshop.',
    SCHOOL_PROJECT: 'Tell us how your time, skills, or experience could support a school project.',
    COMMUNITY: 'There is a place for helping hands. Tell us how you would like to contribute.'
  };
  const updateContext = () => {
    if (context) context.textContent = descriptions[interest?.value] || 'Choose how you would like to help, then share a little about yourself.';
  };
  interest?.addEventListener('change', updateContext);
  updateContext();
  const clearContactError = () => email?.setCustomValidity('');
  email?.addEventListener('input', clearContactError);
  phone?.addEventListener('input', clearContactError);
  form.addEventListener('submit', (event) => {
    if (form.dataset.submitting === 'true') { event.preventDefault(); return; }
    clearContactError();
    if (email && !email.value.trim() && !phone?.value.trim()) {
      email.setCustomValidity('Please enter an email address or phone number so the team can contact you.');
    }
    if (!form.reportValidity()) {
      event.preventDefault();
      if (status) status.textContent = 'Please check the highlighted fields before sending.';
      return;
    }
    form.dataset.submitting = 'true';
    form.setAttribute('aria-busy', 'true');
    if (button) { button.disabled = true; button.setAttribute('aria-busy', 'true'); }
    if (label) label.textContent = 'Sending your offer…';
    if (status) status.textContent = 'Sending your offer securely to the association team…';
  });
  window.addEventListener('pageshow', () => {
    delete form.dataset.submitting;
    form.removeAttribute('aria-busy');
    if (button) { button.disabled = false; button.removeAttribute('aria-busy'); }
    if (label) label.textContent = 'Send my offer';
    if (status) status.textContent = '';
  });
  const summary = form.querySelector('.form-error-summary');
  if (summary) summary.focus();
})();
