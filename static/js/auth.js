(function () {
  function qs(sel, root = document) { return root.querySelector(sel); }
  function qsa(sel, root = document) { return [...root.querySelectorAll(sel)]; }

  function bindAuthLinks(scope) {
    qsa('a.auth-link', scope).forEach(link => {
      link.addEventListener('click', e => {
        e.preventDefault();
        const url = link.getAttribute('href');
        if (url) navigateTo(url, true);
      });
    });
  }
  
  function extractAuthContent(htmlText) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, 'text/html');
    return (doc.querySelector('#auth-content') 
         || doc.querySelector('[data-auth-root]') 
         || doc.body).innerHTML;
  }

  function navigateTo(url, push) {
    const container = qs('#auth-content');
    if (!container) return (window.location.href = url);

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(r => r.ok ? r.text() : Promise.reject())
      .then(html => {
        container.innerHTML = extractAuthContent(html);
        if (push) history.pushState({ authAjax: true }, '', url);
        rebindPageEnhancements(container);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      })
      .catch(() => { window.location.href = url; });
  }


  function rebindPageEnhancements(scope) {
    // Password toggles (login + register)
    [['#togglePassword', '#id_password'],
     ['#togglePassword1', '#id_password1'],
     ['#togglePassword2', '#id_password2']]
    .forEach(([toggleSel, inputSel]) => {
      const toggle = qs(toggleSel, scope);
      const input = qs(inputSel, scope);
      if (toggle && input) {
        toggle.addEventListener('click', () => {
          const type = input.type === 'password' ? 'text' : 'password';
          input.type = type;
          toggle.textContent = type === 'password' ? 'Show' : 'Hide';
        });
      }
    });

    bindAuthLinks(scope);
  }


  window.addEventListener('popstate', () => navigateTo(location.href, false));
  document.addEventListener('DOMContentLoaded', () => bindAuthLinks(document));
})();
