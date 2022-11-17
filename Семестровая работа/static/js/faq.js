const header = document.querySelector('header');
const productToFavorites = document.querySelector('.product__to-favorites');
const favoritesSpan = document.querySelector('#favorites__span');

let inTop = true
window.addEventListener('scroll', () => {
    if (inTop && window.scrollY !== 0) {
        header.classList.toggle('toggle-header');
        inTop = false
    } else if (!inTop && window.scrollY === 0) {
        header.classList.toggle('toggle-header');
        inTop = true
    }
});

const loginRequied = () => alert('Пожалуйста, авторизуйтесь');

const toFavoritesProduct = (id) => {
    if (favoritesSpan.textContent === 'В избранном') {
        favoritesSpan.textContent = 'В избранное';
        productToFavorites.style.color = '#000';
    } else {
        favoritesSpan.textContent = 'В избранном';
        productToFavorites.style.color = 'red';
    }
    $.ajax({
        type: "POST",
        url: '/change-favorites',
        data: {id: id}
    });
};

const toFavoritesShop = (element, id) => {
    $.ajax({
        type: "POST",
        url: '/change-favorites',
        data: {id: id},
        success: element.classList.toggle('in-favorites')
    });
};

const addToCart = (id) => {
    $.ajax({
        type: "POST",
        url: '/append-cart',
        data: {id: id}
    });
}

const deleteFromCart = (id) => {
    $.ajax({
        type: "POST",
        url: '/delete-from-cart',
        data: {id: id}
    });
}

const addToCartFromShop = (element, id) => {
    if (element.textContent === 'В корзину') {
        element.textContent = 'В корзине';
        element.classList.toggle('btn-danger');
        element.classList.toggle('btn-secondary');
        addToCart(id);
    } else {
        element.textContent = 'В корзину';
        element.classList.toggle('btn-danger');
        element.classList.toggle('btn-secondary');
        deleteFromCart(id)
    }
}