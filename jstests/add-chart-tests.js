describe('RadioChoice', function() {
    var choice;
    var form;
    beforeEach(function() {
        form = new AddChartForm();
        choice = new RadioChoice('name', 'statement1', 'statement2', form);
    });
    it('should fire event when clicked', function() {
        spyOn(form, 'nextQuestion');
        expect(choice.hasBeenClicked).toBeFalsy();

        choice.trueButton.fireEvent('click');

        expect(form.nextQuestion).toHaveBeenCalled();
        expect(choice.hasBeenClicked).toBeTruthy();
    });
    it('should fire notify on change', function() {
        spyOn(form, 'nextQuestion');
        spyOn(form, 'answerChanged');

        choice.trueButton.fireEvent('click');
        expect(form.nextQuestion).toHaveBeenCalled();

        choice.trueButton.fireEvent('click');
        expect(form.answerChanged).toHaveBeenCalled();
    });
});

describe('ChartDescription', function() {
    var desc;
    var form;
    beforeEach(function() {
        form = new AddChartForm();
    });
    it('should init properties', function() {
        desc = new ChartDescription(false, false, false);
        expect(desc.contns).toEqual(false);
        expect(desc.cumltv).toEqual(false);
        expect(desc.targtd).toEqual(false);
    });
    it('should create sentence', function () {
        desc = new ChartDescription(false, false, false);
        expect(desc.bits[0]).toEqual('I');
        expect(desc.bits.length).toEqual(4);
    });
    it('should create correct sentences', function() {
        desc = new ChartDescription(true, true, true);
        expect(desc.bits.length).toEqual(6);
        desc = new ChartDescription(false, true, true);
        expect(desc.bits.length).toEqual(6);
    });
});

describe('AddChartForm', function() {
    beforeEach(function() {
    });
    it('should take no args to construct', function() {
        form = new AddChartForm();
        expect(form.questionNum).toEqual(0);
    });
    it('should advance the question', function() {
        form = new AddChartForm();
        expect(form.questionNum).toEqual(0);
        form.nextQuestion();
        expect(form.questionNum).toEqual(1);
    });
    it('should advance three times then create description', function() {
        form = new AddChartForm();
        form.nextQuestion();
        form.nextQuestion();
        expect(form.description).toBeFalsy()
        form.nextQuestion();
        expect(form.description).toBeTruthy()
    });
});
