//$('#dashboard-picker').datepicker("option", "selectDate", true );
//
var forceUpdateDatePicker = function() {
    if (typeof dashboard_router != 'undefined')
    {
        var dates = []
        var fragment = Backbone.history.fragment
        if (fragment == "")
        {
            dates.push(new Date())
        } else {
            frgs = fragment.split(',')
            for (var d in frgs)
            {
                dates.push(new Date(frgs[d]))
            }
        }

        $('#dashboard-picker').multiDatesPicker("resetDates");
        $('#dashboard-picker').multiDatesPicker("addDates", dates );
    }
    collapseToCurrentWeek($('#dashboard-picker'))
}

Backbone.history.bind("all", forceUpdateDatePicker)
$(document).ready(function() {
forceUpdateDatePicker()
})
