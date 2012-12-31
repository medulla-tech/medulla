/*
 * Rounding Raphael JS pie chart data values in percentage
 *
 * Example: [2, 2, 7] will return [16, 16, 68]
 * Sum of number in this list will always be equal to 100.
 *
 * @see:
 *  http://projects.mandriva.org/issues/1994
 *  http://stackoverflow.com/questions/13483430/how-to-make-rounded-percentages-add-up-to-100
 *  http://jsfiddle.net/bruno/4DU2H/1/
 *
 * @param orig: list of values
 * @type: array of integers
 *
 * @target: total we want for the list (100 by default to obtain a percentage)
 * @type: integger
 *
 * @return: original data rounded to percentage
 * @rtype: array
 */

function getPercentageData(orig, target) {
    // If target
    target = typeof target !== 'undefined' ? target : 100;

    var i = orig.length, j = 0, total = 0, change, newVals = [], next, factor1, factor2, len = orig.length, marginOfErrors = [];

    // map original values to new array
    while( i-- ) {
        total += newVals[i] = Math.round( orig[i] );
    }

    change = total < target ? 1 : -1;

    while( total !== target ) {

        // select number that will be less affected by change determined 
        // in terms of itself e.g. Incrementing 10 by 1 would mean 
        // an error of 10% in relation to itself.
        for( i = 0; i < len; i++ ) {

            next = i === len - 1 ? 0 : i + 1;

            factor2 = errorFactor( orig[next], newVals[next] + change );
            factor1 = errorFactor( orig[i], newVals[i] + change );

            if(  factor1 > factor2 ) {
                j = next; 
            }
        }

        newVals[j] += change;
        total += change;
    }


    for( i = 0; i < len; i++ ) { marginOfErrors[i] = newVals[i] && Math.abs( orig[i] - newVals[i] ) / orig[i]; }

        for( i = 0; i < len; i++ ) {
            for( j = 0; j < len; j++ ) {
                if( j === i ) continue;

                var roundUpFactor = errorFactor( orig[i], newVals[i] + 1)  + errorFactor( orig[j], newVals[j] - 1 );
                var roundDownFactor = errorFactor( orig[i], newVals[i] - 1) + errorFactor( orig[j], newVals[j] + 1 );
                var sumMargin = marginOfErrors[i] + marginOfErrors[j];

                if( roundUpFactor < sumMargin) { 
                    newVals[i] = newVals[i] + 1;
                    newVals[j] = newVals[j] - 1;
                    marginOfErrors[i] = newVals[i] && Math.abs( orig[i] - newVals[i] ) / orig[i];
                    marginOfErrors[j] = newVals[j] && Math.abs( orig[j] - newVals[j] ) / orig[j];
                }

                if( roundDownFactor < sumMargin ) { 
                    newVals[i] = newVals[i] - 1;
                    newVals[j] = newVals[j] + 1;
                    marginOfErrors[i] = newVals[i] && Math.abs( orig[i] - newVals[i] ) / orig[i];
                    marginOfErrors[j] = newVals[j] && Math.abs( orig[j] - newVals[j] ) / orig[j];
                }

            }
        }


    function errorFactor( oldNum, newNum ) {
        return Math.abs( oldNum - newNum ) / oldNum;
    }

    console.log( newVals );
    return newVals;
}
