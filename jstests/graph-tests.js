describe('Graph', function() {
    var data = null;
    var graph = null;
    beforeEach(function() {
    });

    it('should be a bar chart when accumulation period is present', function() {
        data = getChartData();
        console.log(data);
        graph = new Graph(data);
        expect(graph.type()).toEqual('column');
    });

    it('should be a line chart when accumulation period is not present', function() {
        data = getChartData(false, true);
        graph = new Graph(data);
        expect(graph.type()).toEqual('line');
    });
});
