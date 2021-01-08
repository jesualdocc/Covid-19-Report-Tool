import{Chart} from 'chart.js';

export class LineGraph2{

  private id:string;
  private data:number[];

  constructor(id:string,data:number[]){
      this.data = data;
      this.id = id;

      this.getChart();
  }

  getChart():Chart{
    const title = "Total Deaths (Last Week Trend)";
    const chart =  new Chart(this.id, {

      type:"line",
      data:{
        labels:['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        datasets:[
        {
          label:'Confirmed Deaths',
          backgroundColor: "green",
          borderColor:"red",
          data:this.data,
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
