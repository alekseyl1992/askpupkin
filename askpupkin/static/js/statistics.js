
function updateChart()
{
     $.ajax({
              type: "GET",
              url: "/chart/",
              data: {}
            })
            .done(function(msg)
            {
                if(msg.length == 0)
                    return;

                msg.unshift(['Tag', 'Questions count', { role: 'style' }]);
                var data = google.visualization.arrayToDataTable(msg);

                var options = {
                    title: 'Questions distribution by tags',
                    vAxis: {title: 'Tag',  titleTextStyle: {color: 'green'}},
                    height: 800,
                    animation: {
                        duration: 1000,
                        easing: 'out',
                      }
                };

                var view = new google.visualization.DataView(data);
                view.setColumns([0, 1,
                    {
                        calc: "stringify",
                        sourceColumn: 1,
                        type: "string",
                        role: "annotation" },
                    2]);

                document.chart.draw(view, options);
            })
            .fail(function(msg)
            {
                alert(msg);
            });
}

jQuery(document).ready(function($) {
    google.load("visualization", "1", {packages:["corechart"],
        callback: function() {
            document.chart = new google.visualization.BarChart(document.getElementById('chart_div'));
            updateChart();
            setInterval(updateChart, 3000);
        }});
})