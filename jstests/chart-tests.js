function getData(noTarget, noAccumulationPeriod, currentProgress) {
    var data = {
        "end": "2011-04-25T00:00:00",
        "chart": {
            "noun": "calories",
            "target": 2100.0,
            "targetOperator": "less than",
            "accumulationPeriod": "day",
            "verb": "eat",
            "id": 20,
            "variableAchievements": true,
            "currentProgress": 0
        },
        "start": "2011-04-15T00:00:00",
        "datapoints": [
             {"start": "2011-04-15T00:00:00",
             "number": 0.0,
             "end": "2011-04-16T00:00:00"},
             {"start": "2011-04-16T00:00:00",
             "number": 0.0,
             "end": "2011-04-17T00:00:00"},
             {"start": "2011-04-17T00:00:00",
             "number": 0.0,
             "end": "2011-04-18T00:00:00"},
             {"start": "2011-04-18T00:00:00",
             "number": 0.0,
             "end": "2011-04-19T00:00:00"},
             {"start": "2011-04-19T00:00:00",
             "number": 0.0,
             "end": "2011-04-20T00:00:00"},
             {"start": "2011-04-20T00:00:00",
             "number": 0.0,
             "end": "2011-04-21T00:00:00"},
             {"start": "2011-04-21T00:00:00",
             "number": 400.0,
             "end": "2011-04-22T00:00:00"},
             {"start": "2011-04-22T00:00:00",
             "number": 0.0,
             "end": "2011-04-23T00:00:00"},
             {"start": "2011-04-23T00:00:00",
             "number": 0.0,
             "end": "2011-04-24T00:00:00"},
             {"start": "2011-04-24T00:00:00",
             "number": 0.0,
             "end": "2011-04-25T00:00:00"}
        ]
    };
    if (noTarget) {
        data.chart.target = '';
        data.chart.targetOperator = '';
    }
    if (noAccumulationPeriod) {
        data.chart.accumulationPeriod = '';
    }
    if (currentProgress != undefined) {
        data.chart.currentProgress = currentProgress;
    }
    return data; 
}
function getChartData(noTarget, noAccumulationPeriod) {
    return new ChartData(getData(noTarget, noAccumulationPeriod));
}

describe('AddCheckInForm', function() {
    var form = null;
    var chart = null;
    beforeEach(function() {
        chart = getChartData().chart;
        form = new AddCheckInForm(chart, true);
    });
    it('should take a chart as argument', function() {
        expect(form.chart.id).toEqual(20);
    });
    it('should have an element representation', function() {
        expect(form.toElement()).not.toBeNull();
    });
    it('should have correct form action', function() {
        expect($(form).getElement('form').get('action')).toEqual('20/checkins/');
    });
    it('should not have a dateInput if date not required', function() {
        form = new AddCheckInForm(chart, false);
        expect($(form).getElement('.check-in-when')).toBeNull();
    });
    it('should have a dateInput if required', function() {
        expect($(form).getElement('.check-in-when')).not.toBeNull();
    });
    it('should have a number input if achievements are variable', function() {
        expect(chart.variableAchievements).toEqual(true);
        expect($(form).getElement('.check-in-number')).not.toBeNull();
    });
    it('should not have a number input if achievements not variable', function() {
        chart.variableAchievements = false;
        form = new AddCheckInForm(chart, true);
        expect($(form).getElement('.check-in-number')).toBeNull();
    });
    it('should fire events for event listeners', function() {
        var fired = false;
        form.addEvent('checkInAdded', function() {fired = true});
        form.fireEvent('checkInAdded');
        expect(fired).toEqual(true);
    });
});

describe('ChartView', function() {
    var chartView = null;
    beforeEach(function() {
        chartView = new ChartView(getChartData());
    });

    it('should return an Element representation', function() {
        expect(chartView.toElement()).not.toBeNull();
    });

    it('should have options with correct links', function() {
        var options = $(chartView).getElement('.chart-options');
        expect(options.getElement('a.graph-link')
            .get('href')).toEqual('#');
        expect(options.getElement('a.retroactive-link')
            .get('href')).toEqual('#');
    });

    it('should have an add check-in form', function() {
        var addCheckIn = $(chartView).getElement('.add-checkin')
            .getElement('form');
        expect(addCheckIn.get('action')).toEqual('20/checkins/');
    });

    it('should have progress indicator', function() {
        var progress = $(chartView).getElement('.progress-indicator');
        expect(progress.getElement('.current-progress').get('class'))
                .toEqual('current-progress succeeding');
    });

    it('should have tracking class on current progress if no target', function() {
        chartView = new ChartView(getChartData(true));
        var progress = $(chartView).getElement('.progress-indicator');
        expect(progress.getElement('.current-progress').get('class'))
                .toEqual('current-progress tracking');
    });

    it('should add the correct number stars', function() {
        var expectedStars = chartView.chartData.datapoints.length
        var stars = $(chartView).getElement('.stars').getChildren();
        expect(stars.length).toEqual(expectedStars);
    });

    it('should have a chart aim sentence', function() {
        var chartAim = $(chartView).getElement('.chart-aim');
        expect(chartAim).not.toBeNull();
        expect(chartAim.get('text')).not.toEqual('');
    });

    it('should alter progress after successful checkin', function() {
        var data = JSON.encode(getData(false, false, 100));
        var response = '{"chartData":' + data + ',"checkIn": {"check_in_date": "2011-04-25T18:50:43.201089", "number": 100.0}}';
        chartView.checkInAdded(response);
        progressText = $(chartView).getElement('.current-progress').get('text')

        expect(progressText).toEqual('Today: 100');
    });

    it('should alter prior success if necessary after checkin', function() {
        var stars = $(chartView).getElement('.stars').getChildren();
        expect(stars.length).toEqual(4);

        var data = JSON.encode(getData(false, false, 3000));
        var response = '{"chartData":' + data + ',"checkIn": {"check_in_date": "2011-04-25T18:50:43.201089", "number": 100.0}}';
        chartView.checkInAdded(response);

        stars = $(chartView).getElement('.stars').getChildren();
        expect(stars.length).toEqual(0);
    });

    it('should alter success indication after successful checkin', function() {
        var progress = $(chartView).getElement('.progress-indicator');
        expect(progress.getElement('.current-progress').get('class'))
                .toEqual('current-progress succeeding');

        var data = JSON.encode(getData(false, false, 3000, 0));
        var response = '{"chartData":' + data + ',"checkIn": {"check_in_date": "2011-04-25T18:50:43.201089", "number": 100.0}}';
        chartView.checkInAdded(response);
        // grab progress again - it will have been replaced
        progress = $(chartView).getElement('.progress-indicator');
        expect(progress.getElement('.current-progress').get('class'))
                .toEqual('current-progress failing');
    });

    it('should have add Check in form after retro button clicked', function() {
        runs(function() {
            this.retroLink = $(chartView).getElement('.retroactive-link');
            expect($(chartView).getElements('.add-checkin').length).toEqual(1);
            this.retroLink.fireEvent('click', {'preventDefault': function(){}});
        });
        waits(100);
        runs(function() {
            expect($(chartView).getElements('.add-checkin').length).toEqual(2);
        });
    });

});

describe('ChartData', function() {
    var chartData = null;
    beforeEach(function() {
        chartData = getChartData();
    });

    it('should keep values from passed in object', function() {
        expect(chartData.hasNext).toEqual(false);
        expect(chartData.hasPrevious).toEqual(false);
    });

    it('should report failure when target not met', function() {
        expect(chartData.isSuccessful(2101)).toEqual(false);

        chartData.chart.targetOperator = "at least";
        expect(chartData.isSuccessful(2001)).toEqual(false);

        chartData.chart.targetOperator = "exactly";
        expect(chartData.isSuccessful(2101)).toEqual(false);
    });

    it('should report success when target met', function() {
        expect(chartData.isSuccessful(2000)).toEqual(true);

        chartData.chart.targetOperator = "at least";
        expect(chartData.isSuccessful(2101)).toEqual(true);

        chartData.chart.targetOperator = "exactly";
        expect(chartData.isSuccessful(2100)).toEqual(true);
    });

    it('should have appropriate sentence for chart', function() {
        var basicChart = {'chart': {"noun": "miles", "target": null,
                "targetOperator": "", "accumulationPeriod": "",
                "verb": "travelled", "id": 20,"variableAchievements": true,
                "currentProgress": 20}};
        chartData = new ChartData(basicChart);
        expect(chartData.aimSentence()).toEqual('I travelled 20 miles');

    });

    it('should have appropriate sentence for non variable chart', function() {
        var basicChart = {'chart': {"noun": "meeting", "target": null,
                "targetOperator": "", "accumulationPeriod": "",
                "verb": "attended", "id": 20,"variableAchievements": false}};
        chartData = new ChartData(basicChart);
        expect(chartData.aimSentence()).toEqual('I attended a meeting');
    });

    it('should have appropriate sentence for accumulating chart', function() {
        var basicChart = {'chart': {"noun": "meetings", "target": null,
                "targetOperator": "", "accumulationPeriod": "week",
                "currentProgress": 0,
                "verb": "attended", "id": 20,"variableAchievements": false}};
        chartData = new ChartData(basicChart);
        expect(chartData.aimSentence()).toEqual('I attended 0 meetings this week');
    });

    it('should have appropriate sentence for daily accumulating chart', function() {
        var basicChart = {'chart': {"noun": "meetings", "target": null,
                "targetOperator": "", "accumulationPeriod": "day",
                "currentProgress": 0,
                "verb": "attended", "id": 20,"variableAchievements": false}};
        chartData = new ChartData(basicChart);
        expect(chartData.aimSentence()).toEqual('I attended 0 meetings today');
    });
});
