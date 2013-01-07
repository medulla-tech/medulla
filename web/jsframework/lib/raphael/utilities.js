/*
 * Express Raphael JS pie chart data values in percentage
 * Sum of numbers in this list will *always* be equal to 100.
 * We don't want a value can be lesser than 1.
 *
 * @see:
 *  http://projects.mandriva.org/issues/1994
 *
 * @param data: list of values
 * @type: array of integers
 *
 * @percent: total we want for the list (100 by default to obtain a percentage)
 * @type: integger
 *
 * @return: original datas in percentage
 * @rtype: array
 */

function getPercentageData(data, percent) {
    // If percent is not defined, set to 100
    var percent = typeof percent !== 'undefined' ? percent : 100;
    var result = new Array();
    var val = 0;
    var decrem = percent;
    var sumData = 0;
    var total = 0;

    // get sum of array
    for (var i = 0; i < data.length; i++) {
        sumData += data[i];
    }

    for (var i = 0; i < data.length; i++) {
        // express value in percentage
        val = Math.round(data[i] * percent / sumData);

        // we don't want a value lesser than 1
        if (val < 1) {
            val = 1;
        }

        // sum of result array must be equal to percent (100 by default)
        if (val < decrem) {
            result.push(val);
        }
        else {
            result.push(percent - total);
        }
        decrem -= val;
        total += val;
    }

    return result;
}
