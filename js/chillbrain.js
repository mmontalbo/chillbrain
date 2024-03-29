$(document).ready(function(){

	var docloc = document.location.href;
	var hashLoc = docloc.search("#");
	if(hashLoc > 0) {
		var firstHash = "" + docloc.substring(docloc.search("#")+1);		
		changeInstructionsText("Your friend sent you the left image.<br/><br/><br/>Of the two images, select the one you like better.<br/><br/><br/> Press 'spacebar' to skip.");
	}else {
		var firstHash = "";
	}

	var imgIndexOffset = 2;
	var preloadedImages = 0;
	var firstPageLoad = true;
	var needNextCombatants = true;
	var cursor = "";
	var displayInstructions = true;
	var firstTwoImagesLoaded = 0;
	var displayMessageText = true;

	//get2Images();

	/*$("img.combatant").bind('load',function() {
		firstTwoImagesLoaded++;
		if(firstTwoImagesLoaded == 2) {
			//alert("done");
			//positionControls();
			preloadImages(4);
		}
	});
	
	$("img.combatant").each(function(){
		if(this.complete) {
			$(this).load();
		}
	});*/
	
	
	$('img.combatant').live("click",function(e) { //----- ways to select winner
		var scaleFactor = 2;
		
		var documentWidth = $(window).width();
		var imgPosition = $(this).offset();
		var imgWidth = $(this).width();
		var imgWidthScaled = $(this).width() * scaleFactor;
		var translateOffset = (documentWidth/2) - (imgPosition.left) - (imgWidth/2);
		var zoomedOffset = documentWidth - imgWidthScaled - (imgWidth) + (imgWidthScaled / 20);

		if($("div#zoomedImage").hasClass("zoomedIn")) {
		
			$("div#content").css("opacity",1);
			$("div#commandCenter").css("opacity",1);
			$("div#titles").css("opacity",1);
		
			$("div#zoomedImage").fadeOut(175);
			
			$("div#zoomTitleBlock").css("top",-100);
			
		} else {
			$("div#content").css("opacity",0.1);
			$("div#commandCenter").css("opacity",0.1);
			$("div#titles").css("opacity",0.1);

			$("div#zoomedImage").fadeIn(300);
			
			$("div#zoomTitleBlock").find("span").text($(this).attr('title'));
			$("div#zoomTitleBlock").find("input").val($(this).attr('permalink'));
			$("div#zoomTitleBlock").each(function(i,el){//Make font as big as possible
				$(el).textfill({ maxFontPixels: 34 })
			}); 
		
			$("img.combatant").css('cursor', function() { //------ adds magnifying glass effect
					 if (jQuery.browser.mozilla) {
						return '-moz-zoom-out';
					}
					else if (jQuery.browser.webkit) {
						return '-webkit-zoom-out';
					}
					else {
					   return 'pointer'; 
					}
			 });
		
			$("div#zoomTitleBlock").css("top",0);
		} 
		$("div#zoomedImage").toggleClass("zoomedIn");
	});
	
	$("div#leftVoteButton").live("click",function(e) {
		/*$("img.leftCombatant").addClass("selected");
		$("img.rightCombatant").addClass("notSelected");
		winnerSelected();
		$(this).css("backgroundColor","#808080");
		*/
	});
	
	$("div#rightVoteButton").live("click",function(e) {
		/*
		$("img.rightCombatant").addClass("selected");
		$("img.leftCombatant").addClass("notSelected");
		winnerSelected();
		$(this).css("backgroundColor","#808080");
		*/
	});
	
	
	$(document).keyup(function(event){
		if($("div#zoomInPicture").css("display") == "none") {
			if(event.keyCode  == 32) { // if 'spacebar' is pressed
				drawGame();
				$("div.control").css("backgroundColor","#808080");
			}
		} else { // zoomedIn
			if(event.keyCode == 27 || event.keyCode  == 32) {
				$("div#zoomInPicture").css({
						display:"none"
				});
			}
		}
	});
	
	
	$("div#zoomInPicture").click(function(e){ //----- closes image unless you click on something else
		if(event.target != this){
			return true;
		} else {
			$("div#zoomInPicture").css({ //make wrapper div visible
				display:"none"
			});
		}
	});
	
	$("img#closeButton").live("click",function(){ //----- ways to hide img
			$("div#content").css("opacity",1);
			$("div#commandCenter").css("opacity",1);
			$("div#titles").css("opacity",1);

			$("div#zoomedImage").fadeOut("fast");
			
			$("div#zoomTitleBlock").css("top",-75);
			
			$("div#zoomedImage").toggleClass("zoomedIn");
	});	
	
	$(window).resize(function() {
  		sizeTitles();
  		//positionControls();
  		//$("div#commandCenter").textfill({ maxFontPixels: "0.75em" })
 
	});

	$('img.combatant').live("hover",function(e) {

		$('img.combatant').removeClass("selected notSelected");
		$(this).addClass("selected");
		//$(this).css("borderColor","#000000");
				
		var pos = $(this).offset();

		var isLeftCombatant = $(this).hasClass("leftCombatant"); //----- apply notSelected class to the other img
		if(isLeftCombatant) {
			$("img.rightCombatant").addClass("notSelected");
		}
		else {
			$("img.leftCombatant").addClass("notSelected");
		}
		
		
		/*if($(this).hasClass("zoomed")) {
			$("img.combatant").css('cursor', function() { //------ adds magnifying glass effect
					 if (jQuery.browser.mozilla) {
						return '-moz-zoom-out';
					}
					else if (jQuery.browser.webkit) {
						return '-webkit-zoom-out';
					}
					else {
					   return 'pointer'; 
					}
			 });
		 } else {*/
		 	$("img.combatant").css('cursor', function() { //------ adds magnifying glass effect
					 if (jQuery.browser.mozilla) {
						return '-moz-zoom-in';
					}
					else if (jQuery.browser.webkit) {
						return '-webkit-zoom-in';
					}
					else {
					   return 'pointer'; 
					}
			 });
		 //}
	
	});
	
	
	
	$("div#leftVoteButton").find("img").live("mouseenter",function(){
		$("img.leftCombatant").css("borderColor","#000000");
	});
	
	$("div#leftVoteButton").live("mouseout",function(){
		$("img.leftCombatant").css("borderColor","#505050");
	});
	
	$("div#rightVoteButton").find("img").live("mouseenter",function(){
		$("img.rightCombatant").css("borderColor","#000000");
	});
	
	$("div#rightVoteButton").live("mouseout",function(){
		$("img.rightCombatant").css("borderColor","#505050");
	});

	$("div#commandCenterText").find("span").bind("webkitTransitionEnd",function(){
		if(displayMessageText) {
			$("div#commandCenterText").find("span").text($("div#commandCenterText").find("span").attr('message'));
			//$("div#commandCenter").textfill({ maxFontPixels: 24 })
			$("div#commandCenterText").find("span").css("opacity","1");
			$("div#commandCenter").find("img").removeClass("jiggle");
		} else {
			$("div#commandCenterText").find("span").html("");
			$("div#commandCenterText").find("span").css("opacity","1");
			displayMessageText = true;
			$("div#commandCenter").find("img").removeClass("jiggle");
			$("div#commandCenterText").find("span").attr('message',"");
		}
	});
	
	$("div#commandCenter").find("img").click(function(){
		$(this).addClass("jiggle");
		window.setTimeout(stopBrainJiggle, 300);
		hideText();
	})
	
	function stopBrainJiggle(){
	$("div#commandCenter").find("img").removeClass("jiggle");
}

function hideText() {
	$("div#commandCenterText").find("span").css("opacity","0");
	displayMessageText = false;
}


//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& FUNCTIONS
//============================================ FUNCTIONS
//############################################ FUNCTIONS
//============================================ FUNCTIONS

		

function get2Images() {
	// Fetch 2 images from server, add to DOM, position them (center horiz/vert), animate them in, preload more

		//$("img.preloaded:eq(0)").attr("trueWidth",$("img.preloaded:eq(0)").width());
		//$("img.preloaded:eq(0)").attr("trueHeight",$("img.preloaded:eq(0)").height());
		$("div#leftTitle span").html($("img.preloaded:eq(0)").attr("title"));
		
		//$("img.preloaded:eq(1)").attr("trueWidth",$("img.preloaded:eq(1)").width());
		//$("img.preloaded:eq(1)").attr("trueHeight",$("img.preloaded:eq(1)").height());
		$("div#rightTitle span").html($("img.preloaded:eq(1)").attr("title"));

	
		$("img.preloaded:first").addClass("leftCombatant combatant").removeClass("preloaded"); //grab first 2 from preloaded stack
		$("img.preloaded:first").addClass("rightCombatant combatant").removeClass("preloaded");	
		//positionImages();
		sizeTitles();
		
		if(firstTwoImagesLoaded >= 2) {
			//preloadImages(4);
		}
	
	
}

function winnerSelected() {
	//animate winner/loser, setup next combatants
	//$("div.controls").css("left",-1200);
	
	var winnerHash = $("img.selected").attr("hash");
	var loserHash = $("img.notSelected").attr("hash");
	
	$("img.selected").remove();
	$("img.notSelected").remove();
	
	getNextCombatants();
	preloadImages(2);
	
	if(imagesArray.length <= 10) {
		data('vote', { img1: winnerHash }, true, function(newImages){addImageDataToImageArray(newImages);});
	} else {
		data('vote', { img1: winnerHash });
	}
	
	//$.post("/vote",{'winner':winnerHash, 'loser':loserHash},function(){},"json");
	//preloadImages(2);

}

function drawGame() {
	//animate winner/loser, setup next combatants
	//$("div.controls").css("left",-1200);

	var imgHashes = []	
	$("img.combatant").each(function(){
		imgHashes.push($(this).attr("hash"));
	});			
	$("img.combatant").remove();
	getNextCombatants();
	preloadImages(2);

	//$.post("/vote", { 'winner' : '', 'loser':'', 'draw[]':imgHashes});
	//		preloadImages(2);
	
	if(imagesArray.length <= 10) {
		data('skip', { img1: imgHashes[0], img2 : imgHashes[1] }, true, function(newImages){addImageDataToImageArray(newImages);});
	} else {
		data('skip', { img1: imgHashes[0], img2 : imgHashes[1] });
	}
}


function getNextCombatants() {
	// change 2 preloaded images into combatants
	
	if($("img.preloaded").size() >= 2) {
		//$("img.preloaded:eq(0)").attr("trueWidth",$("img.preloaded:eq(0)").width());
		//$("img.preloaded:eq(0)").attr("trueHeight",$("img.preloaded:eq(0)").height());
		$("div#leftTitle span").html($("img.preloaded:eq(0)").attr("title"));
		
		//$("img.preloaded:eq(1)").attr("trueWidth",$("img.preloaded:eq(1)").width());
		//$("img.preloaded:eq(1)").attr("trueHeight",$("img.preloaded:eq(1)").height());
		$("div#rightTitle span").html($("img.preloaded:eq(1)").attr("title"));

	
		$("img.preloaded:first").addClass("leftCombatant combatant").removeClass("preloaded"); //grab first 2 from preloaded stack
		$("img.preloaded:first").addClass("rightCombatant combatant").removeClass("preloaded");	
		//positionImages();
		sizeTitles();
		
	}
	else {
		//alert("not enough images preloaded");
	}
	needNextCombatants = false;
	//positionControls();
	

}

function preloadImages(numToPreload) {
	// preload images by fetching from server and putting them in DOM with css hidden
	//imagesArray[0].title
	
	
	for(i=0;i<numToPreload;i++) {
			var el = $("<img />");
			var imageData = imagesArray.shift();
			
			
			el.attr("src","/img?h="+imageData.key);
			el.attr("title",imageData.title);
			el.attr("hash",imageData.key);
			el.attr("permalink",imageData.link);
			//el.attr("elo",imageData.elo);
			el.addClass("preloaded");
			el.attr("id","img_"+imgIndexOffset);
			el.appendTo("div#content");
			/*el.load(function(){
				preloadComplete();
			});*/
			
			imgIndexOffset = imgIndexOffset+1;
		}

}

function preloadComplete() { //-------- DEPRECATED Function!!!
//this function gets called when an image is done loading. Checks needNextCombatants, if true it
	// calls function getNextCombatants. Else, it increments count of images preloaded for next time.
	
	preloadedImages++;
	if (firstPageLoad && needNextCombatants && preloadedImages > 1) {
		getNextCombatants();
		preloadedImages = preloadedImages - 2;
		firstPageLoad = false;
	}
}

function zoomInImage() { // Enlarge selected image
		$("div#zoomInPicture").html(""); //remove previous zoomedPicture
		
		var elShareInput = $("<input />");
		
		elShareInput.attr("value","http://www.chillbrain.com/#"+$("img.selected").attr("hash"));
		elShareInput.appendTo("div#zoomInPicture");
		
		//$("div.controls").css("left",-1200); //hide img controls
		var windowAspetRation = $(window).width() / $(window).height();
		var imgAspectRatio = $("img.selected").width() / $("img.selected").height();
		
		//alert(imgAspectRatio+"");
		$("img.selected").clone().removeClass("combatant selected leftCombatant rightCombatant").appendTo("#zoomInPicture"); //add image to enlarge
		
		if(imgAspectRatio/windowAspetRation < 1) {// window is wider than img, scale by height
			if(imgAspectRatio <= 0.7) { //if img is over 3 times taller than wide, add scroll bar
				$("div#zoomInPicture img").css({
					height:"",
					width:"50%",
					left:"25%",
					top:"5%"
				});
				
				$("div#zoomInPicture input").css({
					top:"0%"
				});
				
				$("div#zoomInPicture").css("overflowY","auto");
			} else { //else just fit image in window by height
			
				var scalingFactor = 0.9*$(window).height() / $("img.selected").attr("trueheight");
				var scaledWidth = $("img.selected").attr("truewidth") * scalingFactor;
				var scaledWidthPercent = (scaledWidth / $(window).width()) * 100;
				var leftMargin = (100 - scaledWidthPercent) / 2;
			
				$("div#zoomInPicture img").css({
					height:"90%",
					width:"",
					left:leftMargin+"%",
					top:"5%"
				});
				
				$("div#zoomInPicture input").css({
					top:"0%"
				});
			}
		} else { //img is wider than window, scale by width
			if(imgAspectRatio >= 3 && $("img.selected").attr("trueheight") >= 150) { //if img is over 3 times wider than tall, add scroll bar
				$("div#zoomInPicture img").css({
					height:"50%",
					width:"",
					left:0,
					top:"25%"
				});
				
				$("div#zoomInPicture input").css({
					top:"10%"
				});
				
				$("div#zoomInPicture").css("overflowX","auto");
			} else {
			
				var scalingFactor = 0.9*$(window).width() / $("img.selected").attr("truewidth");
				var scaledHeight = $("img.selected").attr("trueheight") * scalingFactor;
				var scaledHeightPercent = (scaledHeight / $(window).height()) * 100;
				var topMargin = (100 - scaledHeightPercent) / 2;
			
				$("div#zoomInPicture img").css({
					width:"90%",
					height:"",
					left:"5%",
					top:topMargin+"%"
				});
				
				$("div#zoomInPicture input").css({
					top:topMargin/2-2.5 + "%"
				});
			}
		}
		
		$("div#zoomInPicture img").css('cursor', function() { //------ adds magnifying glass effect
					if (jQuery.browser.mozilla) {
						return '-moz-zoom-out';
					}
					else if (jQuery.browser.webkit) {
						return '-webkit-zoom-out';
					}
					else {
					   return 'pointer'; 
					}
		});
}

function addImageDataToImageArray(imageObject) {
	//alert(imageObject.images);
	//alert(imagesArray.length);
	//console.debug(imagesArray);
	var imageArrayPassed = imageObject.images;
	for(var i in imageArrayPassed)
	{
		var tempImg = imageArrayPassed[i];
		imagesArray.push({ title : tempImg.title, link : tempImg.permalink, key : tempImg.key});
	}
	//alert(imagesArray.length);
}

function sizeTitles() {
	$("div.imgTitle").each(function(i,el){//Make font as big as possible
		$(el).textfill({ maxFontPixels: 38 })
	}); 
	
	var ccWidth = parseFloat($("div#commandCenter").css("width"));
	
	$("div#commandCenter").css("height",0.66*ccWidth);
	
	$("div#commandCenterText").textfill({ maxFontPixels: 14 })

	
}


var _gaq = _gaq || [];
	  _gaq.push(['_setAccount', 'UA-1860596-4']);
	  _gaq.push(['_setDomainName', 'none']);
	  _gaq.push(['_setAllowLinker', true]);
	  _gaq.push(['_trackPageview']);
	
	  (function() {
		var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
		ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
		var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	  })();


});

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function hideImages() {
		/*$("img.leftCombatant").addClass("selected");
		$("img.rightCombatant").addClass("notSelected");
		winnerSelected();
		$(this).css("backgroundColor","#808080");
		
		$("img.rightCombatant").addClass("selected");
		$("img.leftCombatant").addClass("notSelected");
		winnerSelected();
		$(this).css("backgroundColor","#808080");*/
		
		$("img.combatant").css("opacity",0);
		$("div.voteButton").css("opacity",0);
		$("div#titles").css("opacity",0);
		
}

function showImages(){
	$("img.combatant").css("opacity",1);
	$("div.voteButton").css("opacity",1);
	$("div#titles").css("opacity",1);
}

function skipImages() {
	$("img.combatant").css("opacity",0);
	$("div#titles").css("opacity",0);
}

function fadeTextTo(fadeTo) {
		$("div#commandCenter").find("img").addClass("jiggle");
		$("div#commandCenterText").find("span").css("opacity","0");
		//$("div#commandCenter").textfill({ maxFontPixels: 24 })
		//$("div#commandCenter").find("span").css("color","black");
		$("div#commandCenterText").find("span").attr("message",fadeTo);
}



function showMessage(message) {
	fadeTextTo(message);	
}

function showWarning(warning) {
	fadeTextTo(warning);
}

function achievmentUnlocked(achievment){
	fadeTextTo("achievment unlocked");
}
	
;(function($) {
    $.fn.textfill = function(options) {
        var fontSize = options.maxFontPixels;
        var ourText = $('span:visible:first', this);
        var maxHeight = $(this).height();
        var maxWidth = $(this).width();
        var textHeight;
        var textWidth;
        do {
                ourText.css('font-size', fontSize);
                textHeight = ourText.height();
                textWidth = ourText.width();
                fontSize = fontSize - 1;
        } while (textHeight > maxHeight || textWidth > maxWidth && fontSize > 3);
        return this;
    }
})(jQuery);