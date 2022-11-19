var class1 = document.getElementsByClassName('monthlabel')
var class2 = document.getElementsByClassName('monthvalue')

var label = []
for (let i = 0; i < class1.length; i++) {
    label.push(class1[i].innerHTML)
}
var value = []
for (let i = 0; i < class2.length; i++) {
    value.push(parseInt(class2[i].innerHTML))
}


var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: label,
    datasets: [{
      data: value,
      backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
  },
});
