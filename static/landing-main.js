function scaleVideoContainer(){var e=$(window).height()+5,i=parseInt(e)+"px"
$(".homepage-hero-module").css("height",i)}function initBannerVideoSize(e){$(e).each(function(){$(this).data("height",$(this).height()),$(this).data("width",$(this).width())}),scaleBannerVideoSize(e)}function scaleBannerVideoSize(e){var i,n,t=$(window).width(),a=$(window).height()+5
$(e).each(function(){var e=$(this).data("height")/$(this).data("width")
$(this).width(t),1e3>t&&(n=a,i=n/e,$(this).css({"margin-top":0,"margin-left":-(i-t)/2+"px"}),$(this).width(i).height(n)),$(".homepage-hero-module .video-container video").addClass("fadeIn animated")})}!function(e,i,n,t,a,o,d){e.GoogleAnalyticsObject=a,e[a]=e[a]||function(){(e[a].q=e[a].q||[]).push(arguments)},e[a].l=1*new Date,o=i.createElement(n),d=i.getElementsByTagName(n)[0],o.async=1,o.src=t,d.parentNode.insertBefore(o,d)}(window,document,"script","https://www.google-analytics.com/analytics.js","ga"),ga("create","UA-75272324-2","auto"),ga("send","pageview"),$(document).ready(function(){scaleVideoContainer(),initBannerVideoSize(".video-container .poster img"),initBannerVideoSize(".video-container .filter"),initBannerVideoSize(".video-container video"),$(window).on("resize",function(){scaleVideoContainer(),scaleBannerVideoSize(".video-container .poster img"),scaleBannerVideoSize(".video-container .filter"),scaleBannerVideoSize(".video-container video")})})