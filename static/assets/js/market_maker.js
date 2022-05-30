/*

=========================================================
* MarketMaker v2.0
=========================================================

* Copyright 2021

* Developed By Safa Tok (eminsafa [at] yaani.com)

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the

* Software. Please contact us to request a removal. Contact us if you want to remove it.

*/


function main(){

    var page = document.getElementById('active-page-data-container').getAttribute('data-active-page');
    if (page === 'settings'){
        pageSettings();
    }else if(page === 'markets'){
        pageMarkets();
    }else if(page === 'home'){
        pageMarkets();
    }

}


window.onload = (event) => {
    console.log('MarketMaker Loaded!');
    main();
};



/*
=========================================================
* Page Functions
=========================================================
*/

function pageSettings(){

    var exchangeUpdate = function(){
        var selectedExchange = document.getElementById('exchange-selector').value;
        document.getElementsByClassName('exchange-container').forEach(element => element.style.display = 'none');
        document.getElementById(selectedExchange + '-container').style.display = 'block';
    };

    document.getElementById('exchange-selector').addEventListener("change", exchangeUpdate);

}

function pageMarkets(){

    var pairUpdate = function () {
        var selectedExchange = document.getElementById('exchange-selector').value;
        var pairSelector = document.getElementById('exchange-pairs');
        document.getElementById('exchange-pairs').querySelectorAll('*').forEach(element => element.remove());
        var exchangePairs = JSON.parse(document.getElementById('exchange-pair-data-container').getAttribute('data-'+selectedExchange));
        Object.entries(exchangePairs).forEach(([key, value]) => {
            var option = document.createElement('option');
            option.setAttribute('value', key);
            option.innerText = value;
            pairSelector.appendChild(option);
        });
    };
    var currencyUpdate = function () {
        var selectedExchange = document.getElementById('exchange-selector').value;
        var currencySelector = document.getElementById('exchange-currencies');
        document.getElementById('exchange-currencies').querySelectorAll('*').forEach(element => element.remove());
        var exchangeCurrencies = JSON.parse(document.getElementById('exchange-currency-data-container').getAttribute('data-'+selectedExchange));
        Object.entries(exchangeCurrencies).forEach(([key, value]) => {
            var option = document.createElement('option');
            option.setAttribute('valur', key);
            option.innerText = value;
            currencySelector.appendChild(option);
        });
    };

    document.getElementById('exchange-selector').addEventListener('change', pairUpdate);
    document.getElementById('exchange-selector').addEventListener('change', currencyUpdate);

}