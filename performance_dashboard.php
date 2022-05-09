<html>
    <head>
        <meta charset="utf-8">
        <title>Labeling Performance Dashboard</title>
        <script type="text/javascript" src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/chart.js@3.2.1/dist/chart.min.js"></script>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.0.0-beta.1/chartjs-plugin-datalabels.js"></script>
        <script type="text/javascript" src="https://requirejs.org/docs/release/2.3.6/minified/require.js"></script>
        <script type="text/javascript" data-main="mean-average-precision/main.js" src="mean-average-precision/require.js"></script>
    </head>
    <body>
        <div id="lastlogin" width="100%" height="100" style="clear:both;">
            <div style="vertical-align:center;">
                <time id="nowtimetag"></time><br />（Label Studio線上共同標註系統正式上線時間是2021-05-01）
            </div>
            <table style="padding:10px;width:100%;text-align:center;float:left;background-color:#fcf2bc;">
                <thead><tr>
                    <th>ID</th>
                    <th>Last Login(UTC)</th>
                    <th>Labels Created</th>
                    <th style="width:30%;" colspan="5">Annotation Rectangles Created</th>
                    <th style="width:30%;" colspan="5">Annotation Rectangles Updated<br />(created & modified)∈Updated</th>
                </tr><tr>
                    <th></th>
                    <th></th>
                    <th></th><th>all</th><th>7d</th><th>14d</th><th>21d</th><th>30d</th>
                    <th>all</th><th>7d</th><th>14d</th><th>21d</th><th>30d</th>
                </tr></thead>
                <tbody id="lastlogintbody"></tbody>
            </table>
        </div>
        <canvas id="performance_statistics" width="500" height="125"></canvas>
        <canvas id="label_distribution" width="500" height="250"></canvas>
        <script type="text/javascript">
            requirejs(["mean-average-precision/index"], function (mAp) {
                console.log("SUCCESS");
                const groundTruths = [{
                            filename: "image1.jpg",
                            label: "car",
                            left: 22,
                            top: 34,
                            right: 231,
                            bottom: 78,
                        },{
                            filename: "image1.jpg",
                            label: "pedestrian",
                            left: 22,
                            top: 34,
                            right: 231,
                            bottom: 78,
                    }];

                const predictions = [{
                        filename: 'image1.jpg',
                        confidence: 0.9,
                        label: 'car',
                        left: 25,
                        top: 38,
                        right: 201,
                        bottom: 90
                    }, {
                        filename: 'image1.jpg',
                        label: 'pedestrian',
                        confidence: 0.7,
                        left: 32,
                        top: 39,
                        right: 452,
                        bottom: 92
                    }, {
                        filename: 'image1.jpg',
                        confidence: 0.5,
                        label: 'car',
                        left: 541,
                        top: 42,
                        right: 621,
                        bottom: 94
                    }];
                    
                    
                mAP({
                    groundTruths,
                    predictions
                });
            });

        </script>
        <script type="text/javascript">
            var retriveJsonDataConfig = {
                'member': {
                    'url': "http://192.168.10.200:8081/api/organizations/1/memberships",
                    'data': null,
                    'headers': {
                        'Authorization': 'Token **'  //for object property name, use quoted notation shown in second
                    },
                    'method': 'get',
                },
                'labels': {
                    'url': "http://192.168.10.200:8081/api/projects/2/tasks",
                    'data': {
                        'page':1,
                        'page_size':99999,
                    },
                    'headers': {
                        'Authorization': 'Token **'  //for object property name, use quoted notation shown in second
                    },
                    'method': 'get',
                }
            };
            function onlyUnique(value, index, self) {
                return self.indexOf(value) === index;
            }
            function occuranceArray(srcArr) {
                var nbOcc = 0;
                var uniqueArr = srcArr.filter(onlyUnique);
                var occArr = {};
                for (var uniqueArrElement of uniqueArr) {
                    occArr[uniqueArrElement] = 0;
                }
                for (var elementi=0; elementi<srcArr.length; elementi++) {
                    occArr[srcArr[elementi]]++;
                }
                return occArr;
            }
            function retrieveJsonData(config) {
                var result="";
                $.ajax({
                    url: config['url'],
                    async: false,
                    type: config['method'],
                    data: config['data'],
                    headers: config['headers'],
                    dataType: 'json',
                    success: function (data) {
                        result = data;
                    },
                    complete: function(){
                        console.log("Request finished.");
                    }
                });
                return result;
            }
            memberdata = retrieveJsonData(retriveJsonDataConfig['member']);
            labelsdata = retrieveJsonData(retriveJsonDataConfig['labels']);
            //console.log(labelsdata);
            var projectn, recordedAnnotations_n, singleAnnotation_n, recordedAnnotation, username, updated_at;
            var arrUsernames = Array();
            var arrLabelTypes = Array();
            var resCalculateAnnotations = Array();
            const toCheckWrongLabelArr = Array('Moldy','Insect','Pureblack','Sour','Dead','UnlabelledBean','Withered','Shells','MottledSpotted','Broken','Immature','Hulls','Oldpast','Good','Unhulled','ForeignMatter');
            var lastFoundWrongLabels = Array();
            var taskIds = Array();
            var userUpdateRecordTimesOnSingleRectangle = {};
            var userUpdateRecordTimesOnSingleAnnotation = {};
            for (projectn = 0; projectn<labelsdata.length; projectn++) {
                  //console.log('projectn is '+projectn);
                  recordedAnnotations = labelsdata[projectn]['annotations'];
                  for (recordedAnnotations_n = 0; recordedAnnotations_n < recordedAnnotations.length; recordedAnnotations_n++) {
                        username = recordedAnnotations[recordedAnnotations_n]['created_username'].trim();
                        if (!(username in userUpdateRecordTimesOnSingleRectangle)) {
                              userUpdateRecordTimesOnSingleRectangle[username] = Array();
                        }
                        if (!(username in userUpdateRecordTimesOnSingleAnnotation)) {
                              userUpdateRecordTimesOnSingleAnnotation[username] = Array();
                        }
                        updated_at = recordedAnnotations[recordedAnnotations_n]['updated_at'].trim();
                        created_at = recordedAnnotations[recordedAnnotations_n]['created_at'].trim();
                        userUpdateRecordTimesOnSingleAnnotation[username].push(Date.parse(updated_at));
                        lead_time = recordedAnnotations[recordedAnnotations_n]['lead_time'];
                        recordedAnnotation = recordedAnnotations[recordedAnnotations_n]['result'];
                        //console.log('recordedAnnotations_n is '+recordedAnnotations_n);
                        for (singleAnnotation_n = 0; singleAnnotation_n < recordedAnnotation.length; singleAnnotation_n++) {
                              singleAnnotation = recordedAnnotation[singleAnnotation_n];
                              singleAnnotation['username'] = username;
                              singleAnnotation['created_at'] = created_at;
                              singleAnnotation['created_at_timestamp'] = Date.parse(created_at);
                              singleAnnotation['updated_at'] = updated_at;
                              singleAnnotation['updated_at_timestamp'] = Date.parse(updated_at);
                              singleAnnotation['lead_time'] = lead_time;
                              singleAnnotation['created_at'] = created_at;
                              singleAnnotation['task_n'] = labelsdata[projectn]["id"];
                              //console.log('singleAnnotation_n is '+singleAnnotation_n);
                              if (!(toCheckWrongLabelArr.includes(thislabel)) || thislabel=='DamagedBlackBrokenMoldy') {
                                    lastFoundWrongLabels.push(singleAnnotation['task_n']);
                              }
                              for (var thislabel of singleAnnotation['value']['rectanglelabels']) {
                                    //thislabel = singleAnnotation['value']['rectanglelabels'][0];
                                    //DamagedBlackBrokenMoldy,PureBlack,immature,正面看起來是好豆,斑駁豆
                                    arrLabelTypes.push(thislabel);
                                    arrUsernames.push(username);
                              }
                              resCalculateAnnotations.push(singleAnnotation);
                        }
                  }
            }
            //userUpdateRecordTimesOnSingleAnnotation['tingjhenjiang@gmail.com, 2'].map(x => Date.parse(x))
            //const result = words.filter(word => word.length > 6);
            function objectMap(object, mapFn) {
                  return Object.keys(object).reduce(function(result, key) {
                        result[key] = mapFn(object[key])
                        return result
                  }, {})
            }
            function filterOnDays(arrUserUpdateRecords, days, directArray = true, filterOnKey = 'updated_at_timestamp') {
                  var today_in_func = new Date();
                  var currentTimestamp = today_in_func.getTime();
                  var onedaylength = 1000*60*60*24;
                  if (directArray) {
                        filteredArrUserUpdateRecords = arrUserUpdateRecords.filter(arrUserUpdateRecord => arrUserUpdateRecord > (currentTimestamp - onedaylength*days ) );
                        return filteredArrUserUpdateRecords;
                  } else {
                        var newUserUpdateRecords = [];
                        for (var singleElement of arrUserUpdateRecords) {
                              if (singleElement[filterOnKey] > (currentTimestamp - onedaylength*days )) {
                                    newUserUpdateRecords.push(singleElement);
                              }
                        }
                        return newUserUpdateRecords;
                  }
            }
            var today = new Date();
            var currentTimestamp = today.getTime();
            var onedaylength = 1000*60*60*24;
            function filteredResCalculateAnnotations(srcArr, key, checkDays = 7, sumInfo = false) {
                  filteredArr = (JSON.parse(JSON.stringify(srcArr))).filter(element => element[key] > (currentTimestamp - onedaylength*checkDays )  );
                  if (sumInfo===false) {
                        return filteredArr;
                  } else {
                        var authorsArr = [];
                        for (var element of filteredArr) {
                              authorsArr.push(element['username']);
                        }
                        return occuranceArray(authorsArr);
                  }
            }
            /* 標註任務
            userUpdateRecordTimesOnSingleAnnotation7Days = objectMap(userUpdateRecordTimesOnSingleAnnotation, function (v) { return filterOnDays(v,7);});
            userUpdateRecordTimesOnSingleAnnotation14Days = objectMap(userUpdateRecordTimesOnSingleAnnotation, function (v) { return filterOnDays(v,14);});
            userUpdateRecordTimesOnSingleAnnotation30Days = objectMap(userUpdateRecordTimesOnSingleAnnotation, function (v) { return filterOnDays(v,30);});
            */
            
            resCalculateAnnotationsCreatedAllInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'created_at_timestamp', 9999*9999, true);
            resCalculateAnnotationsCreatedIn7DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'created_at_timestamp', 7, true);
            resCalculateAnnotationsCreatedIn14DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'created_at_timestamp', 14, true);
            resCalculateAnnotationsCreatedIn21DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'created_at_timestamp', 21, true);
            resCalculateAnnotationsCreatedIn30DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'created_at_timestamp', 30, true);
            resCalculateAnnotationsUpdAllInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'updated_at_timestamp', 9999*9999, true);
            resCalculateAnnotationsUpdIn7DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'updated_at_timestamp', 7, true);
            resCalculateAnnotationsUpdIn14DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'updated_at_timestamp', 14, true);
            resCalculateAnnotationsUpdIn21DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'updated_at_timestamp', 21, true);
            resCalculateAnnotationsUpdIn30DaysInf = filteredResCalculateAnnotations(resCalculateAnnotations, 'updated_at_timestamp', 30, true);
            //let userUpdateRecordTimesOnSingleAnnotation14Days = JSON.parse(JSON.stringify(userUpdateRecordTimesOnSingleAnnotation));
            //let userUpdateRecordTimesOnSingleAnnotation30Days = JSON.parse(JSON.stringify(userUpdateRecordTimesOnSingleAnnotation));
            lastFoundWrongLabels = lastFoundWrongLabels.filter(onlyUnique)
            nAnnotationOfaUser = occuranceArray(arrUsernames);
            nLabelsOfEachType = occuranceArray(arrLabelTypes);
            //Now time
            var leadingZero = (num) => `0${num}`.slice(-2);
            var formatTime = (date) =>
                [date.getHours(), date.getMinutes(), date.getSeconds()].map(leadingZero).join(':');
            var formatDate = (date) =>
                [date.getFullYear()].concat([date.getMonth()+1,date.getDate()].map(leadingZero) ).join('-');//' UTF+8'
            var appendTrs = "";
            for (var singleMemberdata of memberdata) {
                  var searchInnAnnotationOfaUserKey = singleMemberdata['user']['email']+', '+singleMemberdata['user']['id'];
                  console.log(searchInnAnnotationOfaUserKey);
                  if (searchInnAnnotationOfaUserKey === 'test@gmail.com, 1') {
                        console.log(searchInnAnnotationOfaUserKey);
                        continue;
                  } else {
                        appendTrs += "<tr><td>"+
                              singleMemberdata['user']['username']+
                              "</td><td>"+
                              singleMemberdata['user']['last_activity']+
                              "</td><td>"+
                              nAnnotationOfaUser[searchInnAnnotationOfaUserKey]+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsCreatedAllInf) ? resCalculateAnnotationsCreatedAllInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              //resCalculateAnnotationsCreatedAllInf
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsCreatedIn7DaysInf) ? resCalculateAnnotationsCreatedIn7DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsCreatedIn14DaysInf) ? resCalculateAnnotationsCreatedIn14DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsCreatedIn21DaysInf) ? resCalculateAnnotationsCreatedIn21DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsCreatedIn30DaysInf) ? resCalculateAnnotationsCreatedIn30DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsUpdAllInf) ? resCalculateAnnotationsUpdAllInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              //userUpdateRecordTimesOnSingleAnnotation[searchInnAnnotationOfaUserKey].length+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsUpdIn7DaysInf) ? resCalculateAnnotationsUpdIn7DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsUpdIn14DaysInf) ? resCalculateAnnotationsUpdIn14DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsUpdIn21DaysInf) ? resCalculateAnnotationsUpdIn21DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td><td>"+
                              ((searchInnAnnotationOfaUserKey in resCalculateAnnotationsUpdIn30DaysInf) ? resCalculateAnnotationsUpdIn30DaysInf[searchInnAnnotationOfaUserKey] : "undefined")+
                              "</td>"+
                              "</tr>";
                  }
            }
            $( "#lastlogintbody" ).append( appendTrs );
            $( "#nowtimetag").append( "現在時間是: "+formatDate(today)+' '+formatTime(today)+' UTC+8' );
            var chartOptions = {
                animation: false,
                responsive : true,
                tooltipTemplate: "<%= value %>",
                tooltipFillColor: "rgba(0,0,0,0)",
                tooltipFontColor: "#444",
                tooltipEvents: [],
                tooltipCaretSize: 0,
                onAnimationComplete: function()
                {
                    this.showTooltip(this.datasets[0].bars, true);
                }
            };
            var nAnnotationOfaUserChartID = $('#performance_statistics');
            /*Chart.plugins.register(ChartDataLabels);
            Chart.helpers.merge(Chart.defaults.global.plugins.datalabels, {
                color: '#FE777B'
            });*/
            Chart.defaults.set('plugins.datalabels', {
                color: '#FE777B'
            });
            var nAnnotationOfaUserChart = new Chart(nAnnotationOfaUserChartID, {
                type: 'bar',
                data: {
                    labels: Object.keys(nAnnotationOfaUser),
                    datasets: [{
                        label: '# of annotations created by an author',
                        data: Object.values(nAnnotationOfaUser),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        datalabels: {
                            align: 'end',
                            anchor: 'end',        
                            backgroundColor: function(context) {
                                return context.dataset.backgroundColor;
                            },
                            borderRadius: 4,
                            color: 'white',
                            formatter: Math.round
                        }
                    }
                }
            });

            var nLabelsOfEachTypeID = document.getElementById('label_distribution').getContext('2d');
            var gradientStroke = nLabelsOfEachTypeID.createLinearGradient(0, 0, 0, 100);
            gradientStroke.addColorStop(0, "#328fdebf");
            gradientStroke.addColorStop(1, "#ffffff9e");
            var nLabelsOfEachTypeChart = new Chart(nLabelsOfEachTypeID, {
                type: 'bar',
                data: {
                    labels: Object.keys(nLabelsOfEachType),
                    datasets: [{
                        label: '# of label created',
                        data: Object.values(nLabelsOfEachType),
                        backgroundColor: gradientStroke,
                        borderColor: "#328fde",
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        </script>
    </body>
</html>