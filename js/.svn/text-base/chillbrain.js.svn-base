$(document).ready(function(){

	var smeegle = new infoBox();

	var docloc = document.location.href;
	var hashLoc = docloc.search("#");
	if(hashLoc > 0) {
		var firstHash = "" + docloc.substring(docloc.search("#")+1);
		
		changeInstructionsText("Your friend sent you the left image.<br/><br/><br/>Of the two images, select the one you like better.<br/><br/><br/> Press 'spacebar' to skip.");
		
	}else {
		var firstHash = "";
	}
	
	//http://chillbrain.com/img?h=489f2082483f64a2e105e9837a3dce620e7db205&info
	
	//alert(getUrlVars()["h"]);

	var imgIndexOffset = 0;
	var preloadedImages = 0;
	var firstPageLoad = true;
	var needNextCombatants = true;
	var cursor = "";
	var currentTab = "tab1";
	var displayInstructions = true;

	get2Images();
	//setProgress(50);
	//preloadHistory(9);

	

	$("div.tab").live("click",function(){
		$("div.tab").removeClass("openTab");
		$(this).addClass("openTab");
		currentTab = $(this).attr("id");
		if(currentTab == "tab2") {
			$("div#historyTab").css("display","block");
		}
		else {
			$("div#historyTab").css("display","none");
		}
	});

	
	$('img.combatant').live("click",function(e) { //----- ways to select winner
		//winnerSelected();
		zoomInImage();
	
		/*$("div#zoomInPicture").css({ //make wrapper div visible
			display:"block"
		});*/
		$("div#zoomInPicture").fadeIn("fast");
	});
	
	$("input.leftControl").live("click",function(e) {
		$("img.leftCombatant").addClass("selected");
		$("img.rightCombatant").addClass("notSelected");
		winnerSelected();
		$(this).css("backgroundColor","#808080");
		/*if(displayInstructions) {
			$("div#instructions").fadeOut();
			displayInstructions = false;
		}*/
	});
	
	$("input.rightControl").live("click",function(e) {
		$("img.rightCombatant").addClass("selected");
		$("img.leftCombatant").addClass("notSelected");
		winnerSelected();
		$(this).css("backgroundColor","#808080");
		/*if(displayInstructions) {
			$("div#instructions").fadeOut();
			displayInstructions = false;
		}*/
	});
	
	
	$(document).keyup(function(event){
		if($("div#zoomInPicture").css("display") == "none") {
			//$("div.controls").css({left:-1200}); //----- Hide the controls
			if(event.keyCode  == 32) { // if 'spacebar' is pressed
				drawGame();
				$("div.control").css("backgroundColor","#808080");
				/*if(displayInstructions) {
					$("div#instructions").fadeOut();
					displayInstructions = false;
				}*/
			}
			if(event.keyCode == 27) { // if 'esc' is pressed
				$("div#zoomInPicture").css({
					display:"none"
				});
			}
		} else { // zoomedIn
		if(event.keyCode == 27 || event.keyCode  == 32) {
		
			$("div#zoomInPicture").css({
					display:"none"
			});
		}
		
		}
	});
	
	
	$("div#zoomInPicture").click(function(e){ //----- ways to hide zoom img
		
		if(event.target != this){
			return true;
		} else {
			$("div#zoomInPicture").css({ //make wrapper div visible
				display:"none"
			});
		}
		
	});
	
	$("div#zoomInPicture img").live("click",function(){ //----- ways to hide img
		$("div#zoomInPicture").css({
			display:"none"
		});
		
	});
	
	
	
	$(window).resize(function() {
  		//$('div.controls').css('left',-1200);
  		sizeTitles();
  		positionControls();


	});

	$('img.combatant').live("hover",function(e) {

		$('img.combatant').removeClass("selected notSelected");
		$(this).addClass("selected");
		$(this).css("borderColor","#000000");
		
		var pos = $(this).offset();
		
		if($(this).hasClass("leftCombatant")) { //----- Place controls ontop of the img
			/*$("div.leftControl").css({ 
				left:pos.left+$(this).width()+11,
				top:pos.top+1
			});*/	
			$("input.leftControl").css("backgroundColor","#000000");
			
		} else {
			/*$("div.rightControl").css({
				left:pos.left-70,
				top:pos.top+1
			});*/	
			$("input.rightControl").css("backgroundColor","#000000");
		}
		
		positionControls();

		var isLeftCombatant = $(this).hasClass("leftCombatant"); //----- apply notSelected class to the other img
		if(isLeftCombatant) {
			$("img.rightCombatant").addClass("notSelected");
		}
		else {
			$("img.leftCombatant").addClass("notSelected");
		}
				
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
	
	});
	
	$('img.combatant').live("mouseout",function(e){
		$("input.leftControl").css("backgroundColor","#808080");
		$("input.rightControl").css("backgroundColor","#808080");
		$("img.combatant").css("borderColor","#808080");
	});
	
	$("input.leftControl").live("hover",function(){
		$("img.leftCombatant").css("borderColor","#000000");
		$(this).css("backgroundColor","#000000")
	});
	
	$("input.leftControl").live("mouseout",function(){
		$("img.leftCombatant").css("borderColor","#808080");
		$(this).css("backgroundColor","#808080")
	});
	
	$("input.rightControl").live("hover",function(){
		$("img.rightCombatant").css("borderColor","#000000");
		$(this).css("backgroundColor","#000000")
	});
	
	$("input.rightControl").live("mouseout",function(){
		$("img.rightCombatant").css("borderColor","#808080");
		$(this).css("backgroundColor","#808080")
	});



//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& FUNCTIONS
//============================================ FUNCTIONS
//############################################ FUNCTIONS
//============================================ FUNCTIONS

		

function get2Images() {
	// Fetch 2 images from server, add to DOM, position them (center horiz/vert), animate them in, preload more

	preloadImages(12);
		
}

function winnerSelected() {
//animate winner/loser, setup next combatants
//$("div.controls").css("left",-1200);

var winnerHash = $("img.selected").attr("hash");
var loserHash = $("img.notSelected").attr("hash");

$("img.selected").remove();
$("img.notSelected").remove();

getNextCombatants();
$.post("/vote",{'winner':winnerHash, 'loser':loserHash},function(){},"json");
preloadImages(2);

}

function drawGame() {
	//animate winner/loser, setup next combatants
	//$("div.controls").css("left",-1200);

	var imgHashes = []	
	$("img.combatant").each(function()
	{
		imgHashes.push($(this).attr("hash"));
	});			
		$("img.combatant").remove();
		getNextCombatants();
$.post("/vote", { 'winner' : '', 'loser':'', 'draw[]':imgHashes});
		preloadImages(2);
}


function getNextCombatants() {
	// change 2 preloaded images into combatants
	
	if($("img.preloaded").size() >= 2) {
		$("img.preloaded:eq(0)").attr("trueWidth",$("img.preloaded:eq(0)").width());
		$("img.preloaded:eq(0)").attr("trueHeight",$("img.preloaded:eq(0)").height());
		$("div.leftTitle span").html($("img.preloaded:eq(0)").attr("title"));
		
		$("img.preloaded:eq(1)").attr("trueWidth",$("img.preloaded:eq(1)").width());
		$("img.preloaded:eq(1)").attr("trueHeight",$("img.preloaded:eq(1)").height());
		$("div.rightTitle span").html($("img.preloaded:eq(1)").attr("title"));

	
		$("img.preloaded:first").addClass("leftCombatant combatant").removeClass("preloaded"); //grab first 2 from preloaded stack
		$("img.preloaded:first").addClass("rightCombatant combatant").removeClass("preloaded");	
		positionImages();
		sizeTitles();
	}
	else {
		//alert("no enough images preloaded");
	}
	needNextCombatants = false;
	positionControls();

}

function preloadImages(numToPreload) {
	// preload images by fetching from server and putting them in DOM with css hidden
	
		var imgHashes;
		
		if(firstHash.length > 0) {	//initial hash given so preload the image with given hash, then preload the rest - 1
			var getHashImageData = "/img?h="+firstHash+"&info";
			var getTheRestOfTheImagesString = "/next?p="+(numToPreload)+"&c="+cursor+"&s="+$.cookie("cb_sid");
			
			$.get(getHashImageData, function(data) { //Get data of first img
				hashImgInfo = $.parseJSON(data);
				
				var firstEl = $("<img />");
					
				firstEl.attr("src","/img?h="+firstHash);
				firstEl.attr("title",hashImgInfo.title);
				firstEl.attr("hash",firstHash);
				firstEl.attr("elo",hashImgInfo.rating);
				firstEl.addClass("preloaded");
				firstEl.attr("id","img_"+imgIndexOffset);
				firstEl.appendTo("div#main");
				firstEl.load(function(){
					preloadComplete();
				});
				
				imgIndexOffset = imgIndexOffset+1;
				
				$.get(getTheRestOfTheImagesString, function(data) { //After you load first img, then preload the rest:

					imgHashes = $.parseJSON(data);
								$.cookie("cb_sid",imgHashes.cb_sid, { path: '/' });
		
					cursor = imgHashes.cursor
					for(i=0;i<numToPreload;i++) {
						var el = $("<img />");
						
						el.attr("src","/img?h="+imgHashes.hashes[i]);
						el.attr("title",imgHashes.titles[i]);
						el.attr("hash",imgHashes.hashes[i]);
						el.attr("elo",imgHashes.elos[i]);
						el.addClass("preloaded");
						el.attr("id","img_"+imgIndexOffset);
						el.appendTo("div#main");
						el.load(function(){
							preloadComplete();
						});
						
						imgIndexOffset = imgIndexOffset+1;
					}
				});
				
				
			});			
		} else {
			var getString = "/next?p="+numToPreload+"&s="+$.cookie("cb_sid");
			
			$.get(getString, function(data) { //Hash for pictures

				imgHashes = $.parseJSON(data);
							$.cookie("cb_sid",imgHashes.cb_sid, { path: '/' });
	
				cursor = imgHashes.cursor
				for(i=0;i<numToPreload;i++) {
					var el = $("<img />");
					
					el.attr("src","/img?h="+imgHashes.hashes[i]);
					el.attr("title",imgHashes.titles[i]);
					el.attr("hash",imgHashes.hashes[i]);
					el.attr("elo",imgHashes.elos[i]);
					el.addClass("preloaded");
					el.attr("id","img_"+imgIndexOffset);
					el.appendTo("div#main");
					el.load(function(){
						preloadComplete();
					});
					
					imgIndexOffset = imgIndexOffset+1;
				}
			});	
		}

		
}

function preloadComplete() {
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

function positionImages() { //******* BUG with cached images giving 0 height so calculating top margin is wrong
	//vertically and horizontally align images
	var windowHeight = $(window).height();
	var windowWidth =  $(window).width();
	
	var combatantSpacing = 8; //this is a percentage
	var fixedSpacing = 18;
	//var combatantWidth = (100-(3*combatantSpacing))/2;  //this is a percentage
	var combatantWidth = 0.5*(100-(2*combatantSpacing) - fixedSpacing);
	var rightCombatantPositionLeft = combatantSpacing + fixedSpacing + combatantWidth; //this is a percentage
	
	var el = $("img.leftCombatant");
	el.css({ //Must scale the img by width before you calculate the topMargin below
		width:combatantWidth+"%"
	});
	var el1Height = el.height();
	if(el1Height >= windowHeight) {
		var el1TopMargin = "10";
	} else {
		var el1TopMargin =  (((windowHeight/2) - (el1Height/2)) / windowHeight) * 100;
	}
	el.css({
		top:"15%",
		left:combatantSpacing-3+"%"
	});
	
	var el2 = $("img.rightCombatant");
	el2.css({ //Must scale the img by width before you calculate the topMargin below
		width:combatantWidth+"%"
	});
	var el2Height = el2.height();
	if(el2Height >= windowHeight) {
		var el2TopMargin = "10";
	} else {
		var el2TopMargin =  (((windowHeight/2) - (el2Height/2)) / windowHeight) * 100;
	}
	el2.css({
		top:"15%",
		left:rightCombatantPositionLeft+"%",
		width:combatantWidth+"%"
	});
}

function positionControls() {
	var leftpos = $("img.leftCombatant").offset();
	var rightpos = $("img.rightCombatant").offset();


	$("input.leftControl").css({ //----- Place controls ontop of the img
		left:leftpos.left+$("img.leftCombatant").width()+15,
		top:leftpos.top
	});	
	
	$("input.rightControl").css({ //----- Place controls ontop of the img
		left:rightpos.left-68,
		top:rightpos.top
	});
	
	$("div#instructions").css({
		top:(rightpos.top+150),
		display:"block"
	});
}

function sizeTitles() {
	$("div.title").each(function(i,el){//Make font as big as possible
		$(el).textfill({ maxFontPixels: 38 })
	}); 
	$("div.imgControl").each(function(i,el){//Make font as big as possible
		$(el).textfill({ maxFontPixels: 38 })
	}); 
}

});

function preloadHistory(numToPreload) {
	// preload images by fetching from server and putting them in DOM with css hidden
	
		var imgHashes;
		
		$.get("/next?p="+numToPreload, function(data) { //Hash for pictures
  			imgHashes = $.parseJSON(data);
  			cursor = imgHashes.cursor
  			for(i=0;i<numToPreload;i++) {
				
				var htmlString = "<div class='historyImg'><img src='/img?h=undefined"+"'/><\/div> ";
												
				$("div#historyTab").append(htmlString);

			}
  			
		});		
}



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