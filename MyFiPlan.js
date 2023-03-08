async function populate(){
    const requestURL = './MyFiPlan.json';
    const request = new Request(requestURL);
    const response = await fetch(request);
    const myFiPlan = await response.json();

    populateFiPlan(myFiPlan.data, myFiPlan.info);
}

function monthDiff(d1, d2) {
    var months;
    months = (d2.getFullYear() - d1.getFullYear()) * 12;
    months -= d1.getMonth();
    months += d2.getMonth();
    return months <= 0 ? 0 : months;
}

function forecastFiGoal(curB, curM, avgPerf, goaltarget, endOf_date) {
	var dataset_FiGoal_forecast = [curM];
	var endDate = new Date(endOf_date);
	var startDate = new Date();
	startDate.setMonth(startDate.getMonth() + 1);
	var forecastB = curB;
	
	while (forecastB <= goaltarget) {
		forecastB = forecastB*(1+(avgPerf/12))+curM;
		dataset_FiGoal_forecast.push(curM);
		startDate.setMonth(startDate.getMonth() + 1);
	}
	return (dataset_FiGoal_forecast);
	
}

function totalCurB_FiGoal(goal){
    const envelops = goal.envelops;
    var CurB = 0.0;
    if (Object.keys(envelops).length != 0) {
        for (const envelop in envelops) {
            CurB = CurB + envelops[envelop].current_balance;
            }
    }
    return CurB;
}

function totalCurM_FiGoal(goal) {
    const envelops = goal.envelops;
    var CurM = 0.0;
    if (Object.keys(envelops).length != 0) {
        for (const envelop in envelops) {
            CurM = CurM + envelops[envelop].monthly_invest;
        }
    }
    return CurM;
}

function totalAvgPerf_FiGoal(goal) {
    const envelops = goal.envelops;
    var avgPerf = 0.0;
    if (Object.keys(envelops).length != 0) {
        for (const envelop in envelops) {
            avgPerf = avgPerf + (envelops[envelop].current_balance * (envelops[envelop].expected_growthYield+envelops[envelop].expected_dividendYield));
            }
        avgPerf = avgPerf / totalCurB_FiGoal(goal);
    }
    return avgPerf;
}

function populateFiPlan(jsonData, jsonInfo) {
    const fiplan = document.getElementById('fiplan');
    const goals = jsonData;
    const infos = jsonInfo;

    const totals = document.getElementById('totals');
    const CurTM = document.createElement('p');
    const PowSav = document.createElement('p');
    PowSav.textContent = jsonInfo.current_saving_power;

    var VCurTM = 0.0;

    for (const goal in goals) {
        const myGoal = document.createElement('tr');
        const name = document.createElement('td');
        const type = document.createElement('td');
        const tAmount = document.createElement('td');
        const tAmount_infl = document.createElement('td');
        const tDate = document.createElement('td');
        const avgPerf = document.createElement('td');
        const OptM = document.createElement('td');
        const CurM = document.createElement('td');
        const CurB = document.createElement('td');

        name.textContent = goals[goal].name;
        type.textContent = goals[goal].type;
        tDate.textContent = goals[goal].endOf_date;
        if (goals[goal].type == 'Loan') {
            avgPerf.textContent = 'N/A';
            CurB.textContent = 'N/A';
            VCurTM = VCurTM + goals[goal].monthly_reimb;
            OptM.textContent = goals[goal].monthly_reimb;
            CurM.textContent = goals[goal].monthly_reimb;
            tAmount.textContent = monthDiff(new Date, new Date(goals[goal].endOf_date))*goals[goal].monthly_reimb;
            tAmount_infl.textContent = tAmount.textContent;
        } else {
            tAmount.textContent = goals[goal].goal;
            tAmount_infl.textContent = (goals[goal].goal * Math.pow(1 + infos.expectedYearly_inflation, (monthDiff(new Date, new Date(goals[goal].endOf_date))/12).toFixed(0))).toFixed(2);
            var VavgPerf = 0.0;
            OptM.textContent = 'ToBeCalculated';
            // TODO To be calculated based on current balance which sum of all envelops then PMT type formula
            var VCurM = 0.0;
            var VCurB = 0.0;
            const envelops = goals[goal].envelops;
            if (Object.keys(envelops).length == 0) {
                avgPerf.textContent = 'N/A';
                CurB.textContent = 'N/A';
                CurM.textContent = 'N/A';
            } else {
                for (const envelop in envelops) {
                    VCurM = VCurM + envelops[envelop].monthly_invest;
                    VCurB = VCurB + envelops[envelop].current_balance;
                    VavgPerf = VavgPerf + (envelops[envelop].current_balance * (envelops[envelop].expected_growthYield+envelops[envelop].expected_dividendYield));
                }
                CurB.textContent = VCurB;
                CurM.textContent = VCurM;
                avgPerf.textContent = (VavgPerf / VCurB).toFixed(2);
				forecastFiGoal(VCurB, VCurM,(VavgPerf / VCurB).toFixed(2),goals[goal].endOf_date);
            }
            VCurTM = VCurTM + VCurM;
        }

        CurTM.textContent = VCurTM;

        myGoal.appendChild(name);
        myGoal.appendChild(type);
        myGoal.appendChild(tAmount);
        myGoal.appendChild(tAmount_infl);
        myGoal.appendChild(tDate);
        myGoal.appendChild(CurB);
        myGoal.appendChild(avgPerf);
        myGoal.appendChild(OptM);
        myGoal.appendChild(CurM);
        fiplan.appendChild(myGoal);

        totals.appendChild(CurTM);
        totals.appendChild(PowSav);
    };

// Crating graph timeline axis
	var timeline = [];
	var endDate = new Date(jsonInfo.expectedDateOf_death);
	const date = new Date()
	var monthNameList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
	while (date <= endDate) {
		var monthName = new Date(date).getMonth();
		timeline.push(monthNameList[monthName] + " " + date.getFullYear());
		date.setMonth(date.getMonth() + 1);
	}

// Graph setup
    const data = {
      //labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      labels: timeline,
      /*datasets: [{
        label: 'Weekly Sales',
        data: [300000, 300000, 300000, 300000, 300000, 300000, 90000],
        backgroundColor: 'rgba(255, 26, 104, 0.2)',
        borderColor: 'rgba(255, 26, 104, 1)',
        //tension: 0.4
      },*/
      datasets: [
        {
            label: goals[5].name,
            data: forecastFiGoal(totalCurB_FiGoal(goals[5]), totalCurM_FiGoal(goals[5]), totalAvgPerf_FiGoal(goals[5]), goals[5].goal, goals[5].endOf_date),
            backgroundColor: 'rgba(255, 26, 104, 0.2)',
            borderColor: 'rgba(255, 26, 104, 0.1)',
            fill: true,
            //tension: 0.1
        },
        {
            label: goals[1].name,
            data: forecastFiGoal(-39000000, 205000.0, 0, 40000000, goals[1].endOf_date),
            backgroundColor: 'rgba(200, 26, 104, 0.2)',
            borderColor: 'rgba(200, 26, 104, 0.1)',
            fill: true,
            //tension: 0.1
        }
      ]
    };

// Graph current power saving limit plugin
    const currentSavingPowerLimit = {
        id: 'currentSavingPowerLimit',
        beforeDraw(chart, args, options){
            const { ctx, chartArea: {top, right, bottom, left, width, height},
                scales: {x, y}} = chart;
            ctx.save();

            ctx.strokeStyle = 'green',
            ctx.strokeRect(left, y.getPixelForValue(jsonInfo.current_saving_power), width, 0);

            ctx.font = '12px Arial';
            ctx.fillStyle = 'green';
            ctx.fillText('Current Power Saving', width / 2 + left, y.getPixelForValue(jsonInfo.current_saving_power) - 12);
            ctx.textAlign = 'center';
            ctx.restore();
        }
    }


// Graph config
    const config = {
      type: 'line',
      data,
      options: {
        scales: {
          y: {
            beginAtZero: true,
            stacked: true,
            max: jsonInfo.current_saving_power + 50000,
          }
        }
      },
       plugins: [
        {propagate: true},
        currentSavingPowerLimit
        ]
    };

// Graph render init block
    const myChart = new Chart(
      document.getElementById('myChart'),
      config
    );
}

populate();