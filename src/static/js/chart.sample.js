var randomChartData = function randomChartData(n) {
  var data = [];

  for (var i = 0; i < n; i++) {
    data.push(Math.round(Math.random() * 200));
  }

  return data;
};

var chartColors = {
  "default": {
    primary: '#00D1B2',
    info: '#209CEE',
    danger: '#FF3860'
  }
};

var ctx = document.getElementById('big-line-chart').getContext('2d');

new Chart(ctx, {
  type: 'line',
  data: {
    datasets: 
    [
      {% for item in datos %}
      {
        fill: false,
        borderColor: chartColors["default"].primary,
        borderWidth: 2,
        borderDash: [],
        borderDashOffset: 0.0,
        pointBackgroundColor: chartColors["default"].primary,
        pointBorderColor: 'rgba(255,255,255,0)',
        pointHoverBackgroundColor: chartColors["default"].primary,
        pointBorderWidth: 20,
        pointHoverRadius: 4,
        pointHoverBorderWidth: 15,
        pointRadius: 4,
        data: 
        [ 22,33
{#          {% for data in item %}#}
{#          "{{ data[1] }}",#}
{#          {% endfor %}#}

        ]
      },
      {% endfor %}
    
  ],
    labels: [ "23", "55"
{#       {% for i in range(0, datos|length) %}#}
{#        {% for o in range(0, datos[i]|length) %}#}
{#        "{{ datos[i][o][0] }}",#}
{#       {% endfor %}#}
{#       {% endfor %}#}
    ]
  },
  options: {
    maintainAspectRatio: false,
    legend: {
      display: false
    },
    responsive: true,
    tooltips: {
      backgroundColor: '#f5f5f5',
      titleFontColor: '#333',
      bodyFontColor: '#666',
      bodySpacing: 4,
      xPadding: 12,
      mode: 'nearest',
      intersect: 0,
      position: 'nearest'
    },
    scales: {
      yAxes: [{
        barPercentage: 1.6,
        gridLines: {
          drawBorder: false,
          color: 'rgba(29,140,248,0.0)',
          zeroLineColor: 'transparent'
        },
        ticks: {
          padding: 20,
          fontColor: '#9a9a9a'
        }
      }],
      xAxes: [{
        barPercentage: 1.6,
        gridLines: {
          drawBorder: false,
          color: 'rgba(225,78,202,0.1)',
          zeroLineColor: 'transparent'
        },
        ticks: {
          padding: 20,
          fontColor: '#9a9a9a'
        }
      }]
    }
  }
});
