
//this contents all the settings and links that go in the head tag
class LoadHead extends HTMLElement{
    connectedCallback(){
        this.innerHTML = `
        <meta charset="UTF-8">
        <title>Super Scraper</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <link rel="stylesheet" href="style.css">
        `
    }
}

//this creates the top navigation bar
class Topnav extends HTMLElement{
    connectedCallback(){
        this.innerHTML = `
        <div class="topnav">
            <a><h2>Super Scraper <i class="fa fa-line-chart" style="font-size:24px"></i> </h2></a>
            <a class="active" href="homepage.html"><h3>Home</h3></a>
            <a href="ManagedInvestments.html"><h3>Managed Investments</h3></a>
            <a href="Management.html"><h3>Management</h3></a>
        </div>
        `
    }
}

//this creates the side navigation bar
class Sidenav extends HTMLElement{
    connectedCallback(){
        this.innerHTML = `
        <div class="sidenav">
            <a class="label" href="#home">Super Funds</a>
            <button class="dropdown-btn">Hesta Super  <i class="fa fa-caret-down"></i></button>
            <div class="dropdown-container" id="dropdownID"></div>
            <button class="dropdown-btn">Aware Super  <i class="fa fa-caret-down"></i></button>
            <div class="dropdown-container" id="dropdownID2"></div>
            <button class="dropdown-btn">Telstra Super <i class="fa fa-caret-down"></i></button>
            <div class="dropdown-container" id="dropdownID3"></div>
            <button class="dropdown-btn">Future Super <i class="fa fa-caret-down"></i></button>
            <div class="dropdown-container">
            <a href="#">Historical Data </a>
            </div>
            <button class="dropdown-btn">Uni Super <i class="fa fa-caret-down"></i></button>
            <div class="dropdown-container">
            <a href="#">Balanced Growth</a>
            <a href="#">High Growth</a>
            <a href="#">Conservative Growth</a>
            </div>
            <button class="dropdown-btn">Sun Super <i class="fa fa-caret-down"></i></button>
            <div class="dropdown-container">
            <a href="#">Balanced Growth</a>
            <a href="#">High Growth</a>
            <a href="#">Conservative Growth</a>
        </div>
        `
    }
}

//this creates the manually coded ranking table
class RankingTable extends HTMLElement{
    connectedCallback(){
        this.innerHTML = `
        <h2 style="text-align:left">Super Rankings</h2>
        <div class="container">
            <div class="wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Super Annuation</th>
                            <th>Performance Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="rank">1</td>
                            <td class="team">Uni Super</td>
                            <td class="points">1460</td>
                        </tr>
                        <tr>
                            <td class="rank">2</td>
                            <td class="team">Aware Super</td>
                            <td class="points">1340</td>
                        </tr>
                        <tr>
                            <td class="rank">3</td>
                            <td class="team">Future Super</td>
                            <td class="points">1245</td>
                        </tr>
                        <tr>
                            <td class="rank">4</td>
                            <td class="team">Hesta Super</td>
                            <td class="points">1210</td>
                        </tr>
                        <tr>
                            <td class="rank">5</td>
                            <td class="team">Sun Super</td>
                            <td class="points">1186</td>
                        </tr>
                    </tbody>
                </table>
                
            </div>

        </div>
        `
    }
}

//creating custom elements of the above mentioned features
customElements.define('app-loadhead', LoadHead);
customElements.define('app-topnav', Topnav);
customElements.define('app-sidenav', Sidenav);
customElements.define('app-ranktable', RankingTable);

//the function that creates the dropdown from csv file, call this on load with the sidenav element
function dynamicDrop(){
    document.getElementById("myDropdown").classList.toggle("show");

    window.onclick = function(event) {
        if (!event.target.matches("dropdown-btn")) {
          var dropdowns = document.getElementsByClassName("dropdown-container");
          var i;
          for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
              openDropdown.classList.remove('show');
            }
          }
          console.log("FINDME!:");
          console.log(dropdowns);
        }
    }    
}





