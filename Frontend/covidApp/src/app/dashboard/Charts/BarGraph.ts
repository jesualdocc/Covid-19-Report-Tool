import{Chart} from 'chart.js';

export class BarGraph{

  private id:string;
  private data:number[][];

  constructor(id:string,data:number[][]){
      this.data = data;
      this.id = id;
  }

  getChart():Chart{
    const title = "Total Cases vs Deaths (Last 7 Days)";
    const chart =  new Chart(this.id, {

      type:"bar",
      data:{
        labels:['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        datasets:[{
          label:'Confirmed Cases',
          backgroundColor: "blue",
          borderColor:"green",
          data:this.data[0],
          fill:false
        },
        {
          label:'Confirmed Deaths',
          backgroundColor: "red",
          borderColor:"green",
          data:this.data[1],
          fill:false
        }

      ]
      },

      options: {
          responsive: true,
          title: {
            display: true,
            text: title
          },
          scales: {
              yAxes: [{
                  ticks: {
                      beginAtZero: false
                  },
                  scaleLabel: {
                    display: true,
                    labelString: 'Number of Cases'
                  }
              }]
          }
      }
    });

    return chart;

  }

}
