/*

=========================================================
* MarketMaker v1.0
=========================================================

* Copyright 2021

* Developed By Safa Tok (eminsafa [at] yaani.com)

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the

* Software. Please contact us to request a removal. Contact us if you want to remove it.

*/

// =====    Configuration
var conf = {
    activePage: '',
    pages: [
        'admin_dashboard',
        'dashboard',
        'home',
        'investments',
        'new_investment',
        'register',
        'rewards',
        'settings',
        'transactions',
        'reward_details_public'
    ],
    data: {
    }
};

// =====    API Fetcher
async function fetchData(url, notjson=false, contentType='application/json') {

    try {
        const response = await fetch(url, {
            method: 'GET',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'Content-Type': contentType,
                'Access-Control-Allow-Origin': '*'
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer'
        });
        if(notjson){
            console.log(response);
            return response;
        }else{
            return response.json();
        }
    } catch (e) {
        console.error('ERROR:' + e);
    }
}

// =====    Cookie Fetcher
function getCookie(name) {
    name = name + '=';
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookies = decodedCookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.indexOf(name) == 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
}

// =====    Data Export
function dataExport(page){

    if(page === 'balances'){
        var exportData = [
            ['Currency', 'Free ', 'Used', 'Total', 'Free ($USD)', 'Used ($USD)', 'Total ($USD)']
        ];
        for (let i = 0; i < conf.data.balances.length; i++) {
            var tempArr = []
            var d = conf.data.balances[i];
            tempArr.push(d.currency);
            tempArr.push(d.base_free);
            tempArr.push(d.base_used);
            tempArr.push(d.base_total);
            tempArr.push(d.usd_free);
            tempArr.push(d.usd_used);
            tempArr.push(d.usd_total);
            exportData.push(tempArr);
        }
    }

    let csvContent = "data:text/csv;charset=utf-8,"
        + exportData.map(e => e.join(",")).join("\n");
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "PulseBot_Balances_"+getDate()+".csv");
    document.body.appendChild(link);
    link.click();
}

// =====    Date & Time String
function getDate(){
    const d = new Date();
    return d.getFullYear().toString()+'-'
        +('0' + d.getMonth()).slice(-2)+'-'
        +('0' + d.getDay()).slice(-2)+'_'
        +('0' + d.getHours()).slice(-2)+'.'
        +('0' + d.getMinutes()).slice(-2)+'.'
        +('0' + d.getSeconds()).slice(-2);
}

// =====    Page Detect
function setPageName(){
    const activePage = document.getElementById('active-page-data-container');
    var pageName = activePage.getAttribute('data-active-page');
    conf.activePage = pageName;
    return pageName;
    // @todo may be add page name controller/checker
}

// =====    Time Countdown
function timeCountdown(element, countDownDate) {

    var now = new Date().getTime();
    var distance = countDownDate - now;
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
    element.innerHTML = days + "d " + hours + "h " + minutes + "m ";
    if (distance < 0) {
    element.innerHTML = "<span class='text-danger'>Expired</span>";
    }

}

// =====    Time Countdown Cron
function timeCountdownCron(element){

    var date = element.getAttribute('data-date');
    var countDownDate = new Date(date+" 23:59:00").getTime();
    timeCountdown(element, countDownDate);
    setInterval( timeCountdown(element, countDownDate), 6000);

}

// =====    Export Table of Transactions
function exportTransactions(tableID, week){

    var table = document.getElementById(tableID);

    var title = 'Transactions_Week_'+week+'_';
    var exportData = [
        ['ID', 'E-mail', 'Amount', 'Currency', 'Pair', 'Exchange', 'Wallet Address']
    ];
    var row = '';
    var tempArr = '';
    for (let i = 0; i < table.rows.length; i++) {
        tempArr = [];
        row = table.rows[i];
        tempArr.push(row.getAttribute('data-t-id'));
        tempArr.push(row.getAttribute('data-t-email'));
        tempArr.push(row.getAttribute('data-t-amount'));
        tempArr.push(row.getAttribute('data-t-currency'));
        tempArr.push(row.getAttribute('data-t-pair'));
        tempArr.push(row.getAttribute('data-t-exchange'));
        tempArr.push(row.getAttribute('data-t-wallet'));
        exportData.push(tempArr);
    }


    let csvContent = "data:text/csv;charset=utf-8,"
        + exportData.map(e => e.join(",")).join("\n");
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", title+"_"+getDate()+".csv");
    document.body.appendChild(link);
    link.click();

}

function updateTransactionStatus(week_id, reward_id){
    var status_id = document.getElementById('transaction-update-selector').value;
    if(status_id !== "0"){
        var selected_value = '';
        switch (status_id) {
            case '6':
                selected_value = 'PROCESSED';
                break;
            case '7':
                selected_value = 'PROCESSING';
                break;
            case '8':
                selected_value = 'NOT PROCESSED';
                break;
        }
        var r = confirm("Are you sure to update status to "+selected_value+" ?");
        if (r == true) {
          window.location.href = window.location.origin+'/admin/reward-details/?action=update&reward_id='+reward_id+'&week_id='+week_id+'&status_id='+status_id;
        }
    }

}

async function apiCall(path){
    try {
        const response = await fetch(path, {
            method: 'GET',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json, text/plain',
                'Access-Control-Allow-Origin': '*'
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer'
        });
        return response.json();
    }catch (e) {
        console.error('ERROR: '+e);
    }
}

async function cancelOrder(path, eid){
    var result = await apiCall(path);
    console.log(result);
    if (result.error === true){
        newNotification('red', result.message);
    }else{
        newNotification('green', result.message);
        var cancelButton = document.getElementById('cancel-button-'+eid);
        cancelButton.remove();
        var statusBox = document.getElementById('order-status-'+eid);
        statusBox.innerText = 'CANCELLED';
        statusBox.className = 'btn btn-sm btn-danger';
    }
}

function inputDisableToggle(elementId){
    var element = document.getElementById(elementId);
    var disableStatus = element.getAttribute('disabled');
    if (disableStatus){
        element.removeAttribute('disabled');
    }else{
        element.setAttribute('disabled', true);
    }
}


function startTheBot() {
    var form = document.getElementById('theBotForm');
    form.classList.add('was-validated');
    var totalAllocation = parseFloat(document.getElementById('o1-allocation').value);

    if (document.getElementsByClassName('order-2-param-container')[0].style.display === "block") {
        totalAllocation = totalAllocation + parseFloat(document.querySelector('.order-2-param-container input').value);
    }
    if (document.getElementsByClassName('order-3-param-container')[0].style.display === "block") {
        totalAllocation = totalAllocation + parseFloat(document.querySelector('.order-3-param-container input').value);
    }

    console.log(totalAllocation);
    if (totalAllocation > 100){
        newNotification('red', 'Total Order Allocation can not be greater than 100%');
    } else {
        var rest = form.checkValidity();
        if (rest) {
            document.getElementById("theBotForm").submit();
        } else {
            newNotification('red', 'Form have not validated!');
        }
    }
}


//      Throw New Notification
function newNotification(color, message){
    const notyf = new Notyf({
        position: {
            x: 'right',
            y: 'bottom',
        },
        duration: 2700,
        types: [
            {
                type: 'error',
                background: color,
                icon: {
                    className: 'fas fa-exclamation-circle',
                    tagName: 'span',
                    color: '#fff'
                },
                dismissible: false
            }
        ]
    });
    notyf.open({
        type: 'error',
        message: message
    });

}

// =====    ====   PAGES

// =====    PAGE: New Investment
function pageNewInvestment(){
    const countDownElement = document.getElementById('reward-count-down');
    timeCountdownCron(countDownElement);
}


// =====    Initializer
async function initializer(){
    setPageName();
    console.log(conf.activePage);

    if(conf.activePage === 'new_investment'){
        console.log('New Investment');
        pageNewInvestment();
    }else if(conf.activePage === 'reward_details_public'){
        console.log('<<OK>>');
        pageNewInvestment();
    }
    const countDownElement = document.getElementById('reward-count-down');
    if(![undefined, null].includes(countDownElement)){
        timeCountdownCron(countDownElement);
    }

}


// =====    Validator
function newInvestmentValidation(){
    var form = document.getElementById('new-investment-form');

    if (!form.checkValidity()) {
      console.log('not validated');
    }
    form.classList.add('was-validated');
}
console.log('READY');
// =====    Initialize
/*
$(document).ready(function () {

    initializer();

});
*/


$(document).ready(function() {
    var dt = document.getElementById('datatable');
    if(dt !== null){
        const dataTable = new simpleDatatables.DataTable(dt);
    }
} );


function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;

    // CSV file
    csvFile = new Blob([csv], {type: "text/csv"});

    // Download link
    downloadLink = document.createElement("a");

    // File name
    downloadLink.download = filename;

    // Create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);

    // Hide download link
    downloadLink.style.display = "none";

    // Add the link to DOM
    document.body.appendChild(downloadLink);

    // Click download link
    downloadLink.click();
}

function exportTableToCSV(filename) {
    var csv = [];
    var rows = document.querySelectorAll("#datatable tr");

    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");

        for (var j = 0; j < cols.length; j++)
            row.push(cols[j].innerText);


        csv.push(row.join(";"));
    }

    // Download CSV file
    downloadCSV(csv.join("\n"), filename);
}