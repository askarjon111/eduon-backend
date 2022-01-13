/*
 Template Name: Urora - Bootstrap 4 Admin Dashboard
 Author: Mannatthemes
 Website: www.mannatthemes.com
 File: C3 Chart init js
 */

!function($) {

    var ChartC3 = function() {};

    ChartC3.prototype.init = function (pullik,bepul,combine,yosh,cat,viloyat,foydalanuvchi) {
        //generating chart
        c3.generate({
            bindto: '#chart',
            data: {
                columns: [
                    foydalanuvchi,
                ],
                type: 'bar',
                colors: {
                    Foydalanuvchi: '#2196F3',
                }
            },
            axis: {
                x: {
                    type: 'category',
                    categories:viloyat
                }
            }
        });

        //combined chart
        c3.generate({
            bindto: '#combine-chart',
            data: {
                columns: combine,
                types: {
                    SotilganKurslar: 'bar',
                    Speakerlar: 'bar',
                    Foydalanuvchilar: 'spline',
                    Kurslar: 'line',
                    Videolar: 'bar'
                },
                colors: {
                    SotilganKurslar: '#ff7a5a',
                    Speakerlar: '#3f51b5',
                    Foydalanuvchilar: '#f5b225',
                    Kurslar: '#4f5a76',
                    Videolar: '#009688'
                },
                groups: [
                    ['Speakerlar','Foydalanuvchilar']
                ]
            },
            axis: {
                x: {
                    type: 'category',
                    categories:['Yanvar','Fevral','Mart','Aprel','May','Iyun','Iyul','Avgust','Setiyabr','Oktyabr','Noyabr','Dekabr']
                }
            }
        });

        //roated chart
        c3.generate({
            bindto: '#roated-chart',
            data: {
                columns: [
                ['Revenue', 30, 200, 100, 400, 150, 250],
                ['Pageview', 50, 20, 10, 40, 15, 25]
                ],
                types: {
                    Revenue: 'bar'
                },
                colors: {
                    Revenue: '#3f51b5',
                    Pageview: '#009688'
	            }
            },
            axis: {
                rotated: true,
                x: {
                type: 'categorized'
                }
            }
        });
        //Donut Chart
        c3.generate({
             bindto: '#donut-chart',
            data: {
                columns: yosh,
                type : 'donut'
            },
            donut: {
                title: "Yosh toifasi",
                width: 30,
				label: {
					show:false
				}
            },
            color: {
            	pattern: ['#009688', "#ff7a5a", '#3f51b5', '#2196F3','#251562']
            }
        });
        c3.generate({
             bindto: '#donut-chart2',
            data: {
                columns: cat,
                type : 'donut'
            },
            donut: {
                title: "Kategoriya",
                width: 30,
				label: {
					show:false
				}
            },
            color: {
            	pattern: ['#009688', "#ff7a5a", '#3f51b5', '#2196F3']
            }
        });

        //Pie Chart
        c3.generate({
             bindto: '#pie-chart',
            data: {
                columns: [
                    ['Pullik', pullik],
                    ['Bepul', bepul]
                ],
                type : 'pie'
            },
            color: {
                pattern: ['#3f51b5', '#2196F3']
            },
            pie: {
		        label: {
		          show: false
		        }
		    }
        });

    },
    $.ChartC3 = new ChartC3, $.ChartC3.Constructor = ChartC3

}(window.jQuery),

//initializing
function($) {
    var pullik;
    var bepul;
    $.ajax({
        type:'get',
        url:'charts',
        success:function (data) {
            pullik = data['pullik_course'];
            bepul = data['bepul_course'];
            var combine = data['combine'];
            var viloyat = data['viloyat'];
            var foydalanuvchi = data['foydalanuvchi'];
            var yosh = data['yosh'];
            var cat = data['cat'];
            $.ChartC3.init(pullik,bepul,combine,yosh,cat,viloyat,foydalanuvchi)
        }
    });
    "use strict";

}(window.jQuery);



