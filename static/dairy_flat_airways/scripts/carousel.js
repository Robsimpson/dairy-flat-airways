// These are variables, in case I want to add a card for upcoming flights for a customer
// If time permits I will upgrade this to endless loop

let carousel;
let carouselCards;
let currentCard;

document.addEventListener('DOMContentLoaded', function () {

    carousel = document.getElementsByClassName('carousel-container')[0];
    carouselCards = carousel.children;

    for (let i = 0; i < carouselCards.length; i++) {
        carouselCards[i].setAttribute('data-index', i);
    }
    // Another new thing I have learned today, spread syntax!! The extra gubbins is so I can decide
    // how the navigation buttons should behave based on it being the focus or non focussed card
    [...document.getElementsByClassName('carousel-control-left')].forEach(function (element) {
        element.addEventListener('click', function(event) {
            let trigger_index = event.target.getAttribute('data-index');
            moveLeft(trigger_index);
        });
    });

    [...document.getElementsByClassName('carousel-control-right')].forEach(function (element) {
        element.addEventListener('click', function(event) {
            let trigger_index = event.target.getAttribute('data-index');
            moveRight(trigger_index);
        });
    });

    // This is the initial card that will be displayed
    currentCard = document.getElementsByClassName('carousel-default')[0].getAttribute('data-index');
    //my new position should be the width of the carousel/2 minus the width of the card divided by 2
    //applied to all elements
    selectCardByIndex(currentCard);

    //change the far left, and far right arrows to looping arrows to make it clearer it resets
    carouselCards[0].querySelector('.carousel-control-left').innerHTML = "redo"
    carouselCards[carouselCards.length-1].querySelector('.carousel-control-right').innerHTML = "undo"

});


function moveLeft() {


    if (currentCard === 0) {
        currentCard = carouselCards.length - 1;
    } else {
        currentCard--;
    }

    selectCardByIndex(currentCard);

}

function moveRight() {


    if (currentCard === carouselCards.length - 1) {
        currentCard = 0;
    } else {
        currentCard++;
    }
   selectCardByIndex(currentCard);

}


function selectCardByName(name) {

    for (let card in carouselCards) {
        if (card.getAttribute('id') === name) {
            selectCardByIndex(card.getAttribute('data-index'));
            break;
        }
    }

}

function selectCardByIndex(index) {

    let targetCard = carouselCards[index];

    //my new position should be the width of the carousel/2 minus the width of the card divided by 2
    //applied to all elements

    let newPos = (carousel.offsetWidth / 2) - (targetCard.offsetWidth / 2);
    let moveDistance = newPos - targetCard.offsetLeft;


    //set the initial card to the absolute center of the carousel
    for (let i=0; i<carouselCards.length; i++) {
        carouselCards[i].style.transform = 'translateX(' + moveDistance + 'px)';
    }

}


