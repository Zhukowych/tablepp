window.onload = function() {
    adjustContentMargin();
};

function toggleMenu() {
    var sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
    let window_width = $(window).width();
    if (window_width <= 720) {
        $('div.content').hide();
    }
    adjustContentMargin();
}

function closeSidebar() {
    var sidebar = document.querySelector('.sidebar');
    sidebar.classList.remove('active');
    let window_width = $(window).width();
    if (window_width <= 720) {
        $('div.content').show();
    }
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
