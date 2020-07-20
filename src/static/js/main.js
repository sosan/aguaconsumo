// navbar abrir
Array.from(document.getElementsByClassName('jb-navbar-menu-toggle')).forEach(function (el) {
  el.addEventListener('click', function (e) {
    var dropdownIcon = e.currentTarget.getElementsByClassName('icon')[0].getElementsByClassName('mdi')[0];
    document.getElementById(e.currentTarget.getAttribute('data-target')).classList.toggle('is-active');
    dropdownIcon.classList.toggle('mdi-dots-vertical');
    dropdownIcon.classList.toggle('mdi-close');
  });
});

//nvabar cerrar
Array.from(document.getElementsByClassName('jb-modal')).forEach(function (el) {
  el.addEventListener('click', function (e) {
    var modalTarget = e.currentTarget.getAttribute('data-target');
    document.getElementById(modalTarget).classList.add('is-active');
    document.documentElement.classList.add('is-clipped');
  });
});

// popup cerrar
Array.from(document.getElementsByClassName('jb-modal-close')).forEach(function (el) {
  el.addEventListener('click', function (e) {
    e.currentTarget.closest('.modal').classList.remove('is-active');
    document.documentElement.classList.remove('is-clipped');
  });
});

