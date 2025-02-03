(function($) {

    "use strict";

    /*
    |--------------------------------------------------------------------------
    | Template Name: Vorosha
    | Author: Laralink
    | Developer: Tamjid Bin Murtoza;
    | Version: 1.0.0
    |--------------------------------------------------------------------------
    |--------------------------------------------------------------------------
    | TABLE OF CONTENTS:
    |--------------------------------------------------------------------------
    |
    | 1. Scripts initialization
    | 2. Dynamic Background
    | 3. Mobile Menu
    | 4. Sticky Header
    | 5. One Page Navigation
    | 6. Isotop Initialize
    | 7. Back To Top
    | 8. Footer Sticky
    | 9. Slick Slider
    | 10. Progress Bar
    | 11. Pricing Table
    | 12. Ajax Contact Form And Appointment
    | 13. Mailchimp
    | 14. Modal Video
    | 15. Light Gallery
    | 16. Tamjid Counter
    | 17. Hobble Effect
    | 18. Horizontal parallax
    |
    |--------------------------------------------------------------------------
    */

    /*--------------------------------------------------------------
      1. Scripts initialization
      --------------------------------------------------------------*/
    $.exists = function(selector) {
        return $(selector).length > 0;
    };

    $(window).on("load", function() {
        $(window).trigger("scroll");
        $(window).trigger("resize");
        isotopInit();
    });

    $(document).on("ready", function() {
        $(window).trigger("resize");
        dynamicBackground();
        isotopInit();
        backToTop();
        stickyFooter();
        formValidation();
        slickInit();
        progressBarInit();
        pricingTableInit();
        stickyHeader();
        onePageNavigation();
        mobileMenu();
        mailchimpInit();
        modalVideo();
        lightGallery();
        counterInit();
        hobbleEffect();
        horizontalPrallax();
        new WOW().init();
    });

    $(window).on("resize", function() {
        isotopInit();
        stickyFooter();
    });

    $(window).on("scroll", function() {
        stickyHeader();
        horizontalPrallax();
    });

    /*--------------------------------------------------------------
      2. Dynamic Background
      --------------------------------------------------------------*/

    function dynamicBackground() {
        // Background images
        $('.st-dynamic-bg').each(function() {
            var src = $(this).attr('data-src');
            $(this).css({
                'background-image': 'url(' + src + ')'
            });
        });
    }
    /*--------------------------------------------------------------
      3. Mobile Menu
      --------------------------------------------------------------*/
    function mobileMenu() {
        $('.st-nav').append('<span class="st-munu-toggle"><span></span></span>');
        $('.menu-item-has-children').append('<span class="st-munu-dropdown-toggle"></span>');
        $('.st-munu-toggle').on('click', function() {
            $(this).toggleClass("st-toggle-active").siblings('.st-nav-list').slideToggle();;
        });
        $('.st-munu-dropdown-toggle').on('click', function() {
            $(this).toggleClass('active').siblings('ul').slideToggle();
        });
    }
    /*--------------------------------------------------------------
      4. Sticky Header
      --------------------------------------------------------------*/
    function stickyHeader() {
        var scroll = $(window).scrollTop();
        if (scroll >= 10) {
            $('.st-sticky-header').addClass('st-sticky-active');
        } else {
            $('.st-sticky-header').removeClass('st-sticky-active');
        }
    }

    /*--------------------------------------------------------------
      5. One Page Navigation
      --------------------------------------------------------------*/
    function onePageNavigation() {
        // Click To Go Top
        $('.st-smooth-move').on('click', function() {
            var thisAttr = $(this).attr('href');
            if ($(thisAttr).length) {
                var scrollPoint = $(thisAttr).offset().top - 50;
                $('body,html').animate({
                    scrollTop: scrollPoint
                }, 800);
            }
            return false;
        });

        // One Page Active Class
        var topLimit = 300,
            ultimateOffset = 200;

        $('.st-onepage-nav').each(function() {
            var $this = $(this),
                $parent = $this.parent(),
                current = null,
                $findLinks = $this.find("a");

            function getHeader(top) {
                var last = $findLinks.first();
                if (top < topLimit) {
                    return last;
                }
                for (var i = 0; i < $findLinks.length; i++) {
                    var $link = $findLinks.eq(i),
                        href = $link.attr("href");

                    if (href.charAt(0) === "#" && href.length > 1) {
                        var $anchor = $(href).first();
                        if ($anchor.length > 0) {
                            var offset = $anchor.offset();
                            if (top < offset.top - ultimateOffset) {
                                return last;
                            }
                            last = $link;
                        }
                    }
                }
                return last;
            }

            $(window).on("scroll", function() {
                var top = window.scrollY,
                    height = $this.outerHeight(),
                    max_bottom = $parent.offset().top + $parent.outerHeight(),
                    bottom = top + height + ultimateOffset;

                var $current = getHeader(top);

                if (current !== $current) {
                    $this.find(".active").removeClass("active");
                    $current.addClass("active");
                    current = $current;
                }
            });
        });
    }
    /*--------------------------------------------------------------
      6. Isotop Initialize
      --------------------------------------------------------------*/

    function isotopInit() {

        if ($.exists('.st-isotop')) {
            $('.st-isotop').isotope({
                itemSelector: '.st-isotop-item',
                transitionDuration: '0.60s',
                percentPosition: true,
                originLeft: false,
                masonry: {
                    columnWidth: '.st-grid-sizer'
                }
            });
            /* Active Class of Portfolio*/
            $('.st-isotop-filter ul li').on('click', function(event) {
                $(this).siblings('.active').removeClass('active');
                $(this).addClass('active');
                event.preventDefault();
            });
            /*=== Portfolio filtering ===*/
            $('.st-isotop-filter ul').on('click', 'a', function() {
                var filterElement = $(this).attr('data-filter');
                $(this).parents('.st-isotop-filter').next().isotope({
                    filter: filterElement
                });
            });

        }

    }

    /*--------------------------------------------------------------
      7. Back To Top
      --------------------------------------------------------------*/

    function backToTop() {
        $('#st-backtotop').on('click', function(e) {
            e.preventDefault();
            $('html,body').animate({
                scrollTop: 0
            }, 1000);
        });
    }

    /*--------------------------------------------------------------
      8. Footer Sticky
      --------------------------------------------------------------*/

    function stickyFooter() {
        // Sticky Footer
        var footerHeight = ($('.st-sticky-footer').height());
        var windowHeight = $(window).height();
        var footerHeightPx = footerHeight + 'px';
        $('.st-content').css("margin-bottom", footerHeightPx);
    }
    /*--------------------------------------------------------------
      9. Slick Slider
      --------------------------------------------------------------*/
    function slickInit() {
        $('.st-slider').each(function() {

            // Slick Variable
            var $ts = $(this).find('.slick-container');
            var $slickActive = $(this).find('.slick-wrapper');
            var $sliderNumber = $(this).siblings('.slider-number');

            // Auto Play
            var autoPlayVar = parseInt($ts.attr('data-autoplay'), 10);
            // Auto Play Time Out
            var autoplaySpdVar = 3000;
            if (autoPlayVar > 1) {
                autoplaySpdVar = autoPlayVar;
                autoPlayVar = 1;
            }
            // Slide Change Speed
            var speedVar = parseInt($ts.attr('data-speed'), 10);
            // Slider Loop
            var loopVar = Boolean(parseInt($ts.attr('data-loop'), 10));
            // Slider Center
            var centerVar = Boolean(parseInt($ts.attr('data-center'), 10));
            // Pagination
            var paginaiton = $(this).children().hasClass('pagination');
            // Slide Per View
            var slidesPerView = $ts.attr('data-slides-per-view');
            if (slidesPerView == 1) {
                slidesPerView = 1;
            }
            if (slidesPerView == 'responsive') {
                var slidesPerView = parseInt($ts.attr('data-add-slides'), 10);
                var lgPoint = parseInt($ts.attr('data-lg-slides'), 10);
                var mdPoint = parseInt($ts.attr('data-md-slides'), 10);
                var smPoint = parseInt($ts.attr('data-sm-slides'), 10);
                var xsPoing = parseInt($ts.attr('data-xs-slides'), 10);
            }
            // Fade Slider
            var fadeVar = parseInt($($ts).attr('data-fade-slide'));
            (fadeVar === 1) ? (fadeVar = true) : (fadeVar = false);

            // Slick Active Code
            $slickActive.slick({
                infinite: true,
                autoplay: autoPlayVar,
                dots: paginaiton,
                centerPadding: '0',
                speed: speedVar,
                infinite: loopVar,
                autoplaySpeed: autoplaySpdVar,
                centerMode: centerVar,
                fade: fadeVar,
                rtl:true,
                prevArrow: $(this).find('.slick-arrow-left'),
                nextArrow: $(this).find('.slick-arrow-right'),
                appendDots: $(this).find('.pagination'),
                slidesToShow: slidesPerView,
                responsive: [{
                        breakpoint: 1600,
                        settings: {
                            slidesToShow: lgPoint
                        }
                    },
                    {
                        breakpoint: 1200,
                        settings: {
                            slidesToShow: mdPoint
                        }
                    },
                    {
                        breakpoint: 992,
                        settings: {
                            slidesToShow: smPoint
                        }
                    },
                    {
                        breakpoint: 768,
                        settings: {
                            slidesToShow: xsPoing
                        }
                    }
                ]
            });
        })
    }



    /*--------------------------------------------------------------
      10. Progress Bar
      --------------------------------------------------------------*/
    function progressBarInit() {
        $('.st-progressbar').each(function() {
            var progressPercentage = $(this).data('progress') + "%";
            $(this).find('.st-progressbar-in').css('width', progressPercentage);
        });
    }

    /*--------------------------------------------------------------
      11. Pricing Table
      --------------------------------------------------------------*/
    function pricingTableInit() {
        $('.st-pricing-table.st-style1').hover(
            function() {
                $('.st-pricing-table.st-style1').addClass('st-active');
                $(this).removeClass('st-active');
            },
            function() { $('.st-pricing-table.st-style1').removeClass('st-active') }
        )
    }

    /*--------------------------------------------------------------
      12. Ajax Contact Form And Appointment
      --------------------------------------------------------------*/
    // Contact Form
    function formValidation() {

        $('#st-alert').hide();
        $('#contact-form #submit').on('click', function() {
            var name = $('#name').val();
            var subject = $('#subject').val();
            var phone = $('#phone').val();
            var email = $('#email').val();
            var msg = $('#msg').val();
            var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;

            if (!regex.test(email)) {
                $('#st-alert').fadeIn().html('<div class="alert alert-danger"><strong>هشدار!</strong> لطفاً ایمیل معتبر وارد کنید.</div>');
                return false;
            }

            name = $.trim(name);
            subject = $.trim(subject);
            phone = $.trim(phone);
            email = $.trim(email);
            msg = $.trim(msg);

            if (name != '' && email != '' && msg != '') {
                var values = "name=" + name +
                    "&subject=" + subject +
                    "&phone=" + phone +
                    "&email=" + email +
                    "&msg=" + msg;
                $.ajax({
                    type: "POST",
                    url: "assets/php/contact.php",
                    data: values,
                    success: function() {
                        $('#name').val('');
                        $('#subject').val('');
                        $('#phone').val('');
                        $('#email').val('');
                        $('#msg').val('');

                        $('#st-alert').fadeIn().html('<div class="alert alert-success"><strong>موفق بود!</strong> ایمیل با موفقیت ارسال شد.</div>');
                        setTimeout(function() {
                            $('#st-alert').fadeOut('slow');
                        }, 4000);
                    }
                });
            } else {
                $('#st-alert').fadeIn().html('<div class="alert alert-danger"><strong>هشدار!</strong> همه فیلدها الزامی هستند.</div>');
            }
            return false;
        });

    }


    /*--------------------------------------------------------------
      13. Mailchimp
      --------------------------------------------------------------*/
    // mailchimp start
    function mailchimpInit() {
        if ($('.mailchimp').length > 0) {
            $('.mailchimp').ajaxChimp({
                language: 'fa',
                callback: mailchimpCallback
            });
        }

        function mailchimpCallback(resp) {
            if (resp.result === 'success') {
                $('.subscription-success').html('<i class="fa fa-check"></i><br/>' + resp.msg).fadeIn(1000);
                $('.subscription-error').fadeOut(500);

            } else if (resp.result === 'error') {
                $('.subscription-error').html('<i class="fa fa-times"></i><br/>' + resp.msg).fadeIn(1000);
            }
        }
        $.ajaxChimp.translations.es = {
            'submit': 'در حال ارسال...',
            0: "یک ایمیل تایید برای شما ارسال کرده ایم",
            1: "لطفا یک مقدار وارد کنید",
            2: '«آدرس ایمیل باید حاوی یک @ باشد»',
            3: "بخش دامنه آدرس ایمیل نامعتبر است (بخش بعد از @: )",
            4: "بخش نام کاربری آدرس ایمیل نامعتبر است (قسمت قبل از @: )",
            5:'این آدرس ایمیل جعلی یا نامعتبر به نظر می رسد. لطفا یک آدرس ایمیل حقیقی وارد کنید'
        };

    }

    /*--------------------------------------------------------------
      14. Modal Video
      --------------------------------------------------------------*/
    function modalVideo() {
        $(document).on('click', '.st-video-open', function(e) {
            e.preventDefault();
            var video = $(this).attr('href');
            $('.st-video-popup-container iframe').attr('src', video);
            $('.st-video-popup').addClass('active');

        });
        $('.st-video-popup-close, .st-video-popup-layer').on('click', function(e) {
            $('.st-video-popup').removeClass('active');
            $('html').removeClass('overflow-hidden');
            $('.st-video-popup-container iframe').attr('src', 'about:blank')
            e.preventDefault();
        });
    }

    /*--------------------------------------------------------------
      15. Light Gallery
      --------------------------------------------------------------*/

    
    function lightGallery() {
        $('.st-lightgallery').each(function() {
            $(this).lightGallery({
                selector: '.st-lightbox-item',
                subHtmlSelectorRelative: false,
                thumbnail: false,
                mousewheel: true
            });
        });
    }


    /*--------------------------------------------------------------
      16. Tamjid Counter
      --------------------------------------------------------------*/
    function counterInit() {
        $('.st-counter').tamjidCounter({
            duration: 700
        });
    }

    /*--------------------------------------------------------------
      17. Hobble Effect
      --------------------------------------------------------------*/
    function hobbleEffect() {
        $(document).on('mousemove', '.st-hobble', function(event) {
            var halfW = (this.clientWidth / 2);
            var halfH = (this.clientHeight / 2);
            var coorX = (halfW - (event.pageX - $(this).offset().left));
            var coorY = (halfH - (event.pageY - $(this).offset().top));
            var degX = ((coorY / halfH) * 6) + 'deg';
            var degY = ((coorX / halfW) * -6) + 'deg';
            var degX1 = ((coorY / halfH) * -50) + 'px';
            var degY1 = ((coorX / halfW) * 50) + 'px';
            var degX2 = ((coorY / halfH) * -25) + 'px';
            var degY2 = ((coorX / halfW) * 25) + 'px';
            var degX3 = ((coorY / halfH) * 15) + 'deg';
            var degY3 = ((coorX / halfW) * -15) + 'deg';

            $(this).find('.st-hover-layer').css('transform', function() {
                return 'perspective( 800px ) translate3d( 0, -2px, 0 ) rotateX(' + degX + ') rotateY(' + degY + ')';
            });
            $(this).find('.st-hover-layer1').css('transform', function() {
                return 'perspective( 800px ) translate3d( 0, 0, 0 ) rotateX(' + degX + ') rotateY(' + degY + ')';
            });
            $(this).find('.st-hover-layer4').css('transform', function() {
                return 'perspective( 800px ) translate3d( 0, 0, 0 ) rotateX(' + degX3 + ') rotateY(' + degY3 + ')';
            });
            $(this).find('.st-hover-layer2').css('transform', function() {
                return 'perspective( 800px ) translateX(' + degX1 + ') translateY(' + degY1 + ')';
            });
            $(this).find('.st-hover-layer3').css('transform', function() {
                return 'perspective( 800px ) translateX(' + degX2 + ') translateY(' + degY2 + ')';
            });
        }).on('mouseout', '.st-hobble', function() {
            $(this).find('.st-hover-layer').removeAttr('style');
            $(this).find('.st-hover-layer1').removeAttr('style');
            $(this).find('.st-hover-layer2').removeAttr('style');
            $(this).find('.st-hover-layer3').removeAttr('style');
            $(this).find('.st-hover-layer4').removeAttr('style');
        });
    };

    /*--------------------------------------------------------------
      18. Horizontal parallax
      --------------------------------------------------------------*/
    function horizontalPrallax() {
        $('.st-parallax-shape-wpra').each(function() {
            var windowScroll = $(document).scrollTop(),
                windowHeight = $(window).height(),
                barOffset = $(this).offset().top,
                barHeight = $(this).height(),
                barScrollAtZero = windowScroll - barOffset + windowHeight,
                barHeightWindowHeight = windowScroll + windowHeight,
                barScrollUp = barOffset <= (windowScroll + windowHeight),
                barSctollDown = barOffset + barHeight >= windowScroll;

            if (barSctollDown && barScrollUp) {
                var calculadedHeight = barHeightWindowHeight - barOffset;
                var calcWindowScroll = ((calculadedHeight / 15));
                var calcWindowScroll2 = ((calculadedHeight / 5));
                $(this).find('.st-parallax-shape.st-style1').css('margin-top', ("-" + calcWindowScroll2 + "px"));
                $(this).find('.st-parallax-shape.st-style1').css('margin-right', ("-" + calcWindowScroll + "px"));
                $(this).find('.st-parallax-shape.st-style2').css('transform', `rotate(${calcWindowScroll}deg)`);
            }
        });
    }
    /*--------------------------------------------------------------
      ###. Template Settings
      --------------------------------------------------------------*/


      $(document).on("ready", function() {
        $('.st-accent-color').on('click', function() {
            var colorClass = $(this).attr('data-color');
            $('body').removeClass('st-green st-blue st-indigo st-purple st-orange st-red st-teal st-yellow').addClass(colorClass);
        })
        $('.st-accent-color').on('click', function() {
            $(this).addClass('active').siblings().removeClass('active');
        })
        $('.st-color-mode-btn').on('click', function() {
            $(this).addClass('st-active').siblings().removeClass('st-active');
        })
        $('.st-settings-switch').on('click', function() {
            $(this).parents('.st-settings-wrap').toggleClass('active');
        })
        $('.st-night-color').on('click', function() {
            $('body').addClass('st-night-mode')
        })
        $('.st-day-color').on('click', function() {
            $('body').removeClass('st-night-mode')
        })
    });

})(jQuery); // End of use strict

 document.addEventListener("DOMContentLoaded", function () {
      const countdownElements = document.querySelectorAll(".countdown");
    
      countdownElements.forEach(function (element) {
        // دریافت تاریخ نهایی از data-attribute
        const deadline = new Date(element.dataset.deadline).getTime();
    
        // به‌روزرسانی شمارش معکوس هر یک ثانیه
        const interval = setInterval(function () {
          const now = new Date().getTime();
          const timeRemaining = deadline - now;
    
          // اگر زمان تمام شده است
          if (timeRemaining <= 0) {
            clearInterval(interval);
            element.innerHTML = "کمپین به پایان رسیده است!";
            return;
          }
    
          // محاسبه روز، ساعت، دقیقه و ثانیه
          const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
          const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
    
          // نمایش شمارش معکوس
          element.innerHTML = `${days} روز ${hours} ساعت ${minutes} دقیقه ${seconds} ثانیه`;
        }, 1000);
      });
    });
    