// Minimal AJAX navigation between login and register to avoid full rerender
(function () {
  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function bindAuthLinks(scope) {
    qsa('a.auth-link', scope).forEach(function (link) {
      link.addEventListener('click', function (e) {
        // Only intercept left-click without modifier keys
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        e.preventDefault();
        var url = link.getAttribute('href');
        if (!url) return;
        navigateTo(url, true);
      });
    });
  }

  function extractAuthContent(htmlText) {
    // Parse returned HTML and extract the inner of #auth-content if present
    var parser = new DOMParser();
    var doc = parser.parseFromString(htmlText, 'text/html');
    var container = doc.querySelector('#auth-content');
    if (container) {
      return container.innerHTML;
    }
    // Fallback: try to get the main block content if the id isn't found
    var main = doc.querySelector('[data-auth-root]') || doc.body;
    return main ? main.innerHTML : htmlText;
  }

  function rebindPageEnhancements(scope) {
    // Rebind password toggles for login
    var toggle = qs('#togglePassword', scope);
    var pwd = qs('#id_password', scope);
    if (toggle && pwd) {
      toggle.addEventListener('click', function () {
        var type = pwd.getAttribute('type') === 'password' ? 'text' : 'password';
        pwd.setAttribute('type', type);
        this.textContent = type === 'password' ? 'Show' : 'Hide';
      });
    }
    // Rebind password toggles for register
    var t1 = qs('#togglePassword1', scope);
    var t2 = qs('#togglePassword2', scope);
    var p1 = qs('#id_password1', scope);
    var p2 = qs('#id_password2', scope);
    if (t1 && p1) {
      t1.addEventListener('click', function () {
        var type = p1.getAttribute('type') === 'password' ? 'text' : 'password';
        p1.setAttribute('type', type);
        this.textContent = type === 'password' ? 'Show' : 'Hide';
      });
    }
    if (t2 && p2) {
      t2.addEventListener('click', function () {
        var type = p2.getAttribute('type') === 'password' ? 'text' : 'password';
        p2.setAttribute('type', type);
        this.textContent = type === 'password' ? 'Show' : 'Hide';
      });
    }

    // Rebind auth links inside the newly injected content
    bindAuthLinks(scope);
  }

  function navigateTo(url, push) {
    var container = qs('#auth-content');
    if (!container) { window.location.href = url; return; }
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) return;
      if (xhr.status >= 200 && xhr.status < 300) {
        var html = xhr.responseText || '';
        var inner = extractAuthContent(html);
        container.innerHTML = inner;
        if (push) {
          try { history.pushState({ authAjax: true }, '', url); } catch (_) {}
        }
        rebindPageEnhancements(container);
        try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (_) { window.scrollTo(0,0); }
      } else {
        window.location.href = url;
      }
    };
    xhr.onerror = function () { window.location.href = url; };
    xhr.send();
  }

  // Handle back/forward navigation
  window.addEventListener('popstate', function () {
    var url = window.location.href;
    navigateTo(url, false);
  });

  // Initial bind
  document.addEventListener('DOMContentLoaded', function () {
    bindAuthLinks(document);
  });
})();


