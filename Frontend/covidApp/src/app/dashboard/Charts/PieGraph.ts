import{Chart} from 'chart.js';

export class PieGraph{

  data:number[];
  id:string;

  constructor(id:string,data:number[]){
    this.data = data;
    this.id = id;
  }

  getChart():Chart{
    const title = "Active/Recovered Cases vs Deaths";

    var casesMinusDeaths = this.data[0] - this.data[1];

    var data = [casesMinusDeaths, this.data[1]];

    const chart =  new Chart(this.id, {

      type:"pie",
      data:{
        labels:['Active/Recovered Cases', 'Confirmed Deaths'],
        datasets:[{
          label:'Daily',
          backgroundColor: ["blue","red"],
          borderColor:"green",
          data:data
        }

      ]
      },

      options: {
        responsive: true,
				title: {
					display: true,
					text: title
        },
        tooltips: {
          enabled: true
     },
          scales: {
              yAxes: [{
                  ticks: {
                      display:false,
                      beginAtZero: false
                  }
              }]
          }
      }
    });

    return chart;

  }

}
