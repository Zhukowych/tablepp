window.onload = function() {
adjustContentMargin();
};

function toggleMenu() {
var sidebar = document.querySelector('.sidebar');
sidebar.classList.toggle('active');
adjustContentMargin();
}

function closeSidebar() {
var sidebar = document.querySelector('.sidebar');
sidebar.classList.remove('active');
adjustContentMargin();
}

function adjustContentMargin() {
var sidebar = document.querySelector('.sidebar');
var content = document.querySelector('.content');
if (sidebar.classList.contains('active')) {
    content.style.marginLeft = '250px';
} else {
    content.style.marginLeft = '0';
}
}
