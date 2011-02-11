
/**
 * 
 * Chillbrain core. Put the entire MVC structure in here.
 * 
 */

if(window.location.hash) {
	window.location.hash = "load/" + window.location.hash.substring(1);
}

$(function() 
{	
	var ImageModel = Backbone.Model.extend({
		defaults: {
			"id" : "",
			"title" : "...",
			"permalink" : "",
			"src" : "",
		}
	});
	
	var globalEvents = new Object();
	_.extend(globalEvents, Backbone.Events);
	
	 var Feed = Backbone.Collection.extend({
		model: ImageModel,
	    fetchSize : 10,
	      
	    // point to custom feed url
	    url: function() {
      		return '/feed?n=' + this.fetchSize;
	    },

	    // triggered on a vote or skip event, returns two Images to be
	    // displayed
	    getNextImages : function() {		
	    	var nextImages = _.first(this.models,10);
			this.remove(nextImages);

			this.fetchMoreImages(this.fetchSize);
			return nextImages;
	    },

	    // fetch n more images from the server and add them to the
	    // collection
	    fetchMoreImages : function() {	
			this.fetch({
				success : function() { 
					globalEvents.trigger("fetchComplete"); 
				},
			});
	    }
	});	

    var UIController = Backbone.Controller.extend({
    	feed : null,
    	preloaded : new Array(),
    	leftImage : null,
    	rightImage: null,
    	index : 1,
	
    	initialize : function() {
    		_.bindAll(this, "transactionSuccess", "fetchComplete", "vote", "skip", "share");
    	
    		// setup global bindings for this object
    		globalEvents.bind("fetchComplete", this.fetchComplete);
    		globalEvents.bind("transactionSuccess", this.transactionSuccess);
    		
    		globalEvents.bind("vote", this.vote);
    		globalEvents.bind("skip", this.skip);
    		globalEvents.bind("share", this.share);
    		
    		this.feed = new Feed;
    	},
    	  
    	// the different controller mappings live here
	    routes : {
    		"first" 				: "learningOne",
			"second"				: "learningTwo",
			"third" 				: "learningThree",
			":image1,:image2"  		: "next",
			"load/:image1,:image2"	: "landing"
    	},

	    learningOne : function() {
			
	    },
		
	    learningTwo : function() {
			
	    },
		
	    learningThree : function() {
			
	    },
	    
	    fetchComplete : function() {
	    	
	    },
	    
	    landing : function(image1, image2) {
	    	
	    },
	    
	    // Setup the page. This will get the list of images (which have been rendered into the model)
	    // and bind them to the already showing images as well as pre-load the rest of the images
	    setup : function() {
	    	var nextImages = this.feed.getNextImages();   
	    	
	    	var left = nextImages.shift();
	    	var right = nextImages.shift();

	    	this.leftImage = new UI.LeftImage({  model: left, el : $("#"+left.id) }).render();
	    	this.rightImage = new UI.RightImage({ model: right, el : $("#"+right.id) }).render();
	    	
	    	this.preload(nextImages);
	    },
	    
	    preload : function(images) {
	    	for(var i=0; i < images.length; i++) 
	    		this.preloaded.push(new UI.PreloadedImage({ model : images[i] }).render());
	    },
	      
	    next : function(image1, image2) {
	    	this.leftImage = this.leftImage.replace(this.preloaded.pop());
	    	this.rightImage = this.rightImage.replace(this.preloaded.pop());
	    	
	    	if(this.preloaded.length < 5)
	    		this.preload(this.feed.getNextImages());
	    },
		
	    vote : function(img) {
	    	async("/vote?img=" + img);
	    	this.transactionSuccess();
	    },
		
	    skip : function(img, img2) {
	    	async("/skip?img=" + img + "&img2=" + img2);
	    },
		
	    share : function(img) {
	    	async("/share?img=" + img);
	    },	
	    
	    transactionSuccess : function(callback) {
	    	window.location.hash = [this.leftImage.model.get("id"), this.rightImage.model.get("id")].join(",");
	    }
    });
	
	// make UI namespace for View element
	var UI = new Object();
	UI.VoteButton = Backbone.View.extend({
		img : null,
		bind : function(img) {
			this.img = img;
		},
		
		events : {
			"click" : "vote",
			"mouseover" : "hover",
			"mouseout" : "unhover",
		},
		
		vote : function() {
			globalEvents.trigger("vote", $(this.img.el).attr("id"));
		},
		
		hover : function() {
			$(this.img.el).css("borderColor","#000000");
			this.img.controlBar.css({
			 		'borderColor':'#000000',
			 		'backgroundColor':'#000000'
			 });
		},
		
		unhover : function() {
			$(this.img.el).css("borderColor","#575757");
			this.img.controlBar.css({
			 		'borderColor':'#575757',
			 		'backgroundColor':'#575757'
		 });
		}
	});
	
	UI.Image = Backbone.View.extend({
		tagName : "img",
	    render : function() {
			// render image
			$(this.el).attr(this.model.toJSON());
			$(this.el).addClass(this.className);
				
			// render title
			$(this.title).text(this.model.get("title"));	
			  
			this.wrapper.append(this.el);
			return this;
		},
		
	    // utility to return the element
	    html : function() {
			return this.el;
	    },	
	});
	
    // View for a preloaded image. This just sets the tag name and class
	// name to ensure the image will be created as the proper
    // tag type with the correct styling when it is rendered
    UI.PreloadedImage = UI.Image.extend({
    	className : "preloaded",
    	render : function() {
    		$("#content").append(this.el);
    		return this;
    	}
	 });
	
     // View for a shown image. These have vote buttons associated with them.
     // Note: Subclasses MUST contain a voteButton attribute or there will be
	 // bad things
     var currentZoomedImage = {
         zoomed : false,
         image : null,
         set : function(image) {
    	 	this.image = image;
    	 	this.zoomed = true;
     	 },
     	 reset : function() {
     		this.image = null;
     		this.zoomed = false;
     	 },
     	 isZoomed : function() {
     		return this.zoomed; 
     	 },
     	 canZoom : function(image) {
     		return this.image == null && this.zoomed == false; 
     	 },
     };
     _.bindAll(currentZoomedImage);
     
     UI.ShowingImage = UI.Image.extend({
    	 zoomedIn : false,
    	 zoomedTitle : $("div#zoomTitleBlock").find("span"),
    	 zoomedPermalink : $("div#zoomTitleBlock").find("a"),
    	 
    	 render : function() {
    	     	 
    	 	_.bindAll(this,'parentHover','parentUnhover');
    	 
    	 	this.wrapper.live('mouseover',this.parentHover);
    	 	this.wrapper.live('mouseout',this.parentUnhover);
    	 
    	 	$(this.el).removeClass("preloaded");
		 	this.voteButton.bind(this);
		  	return new UI.Image().render.call(this);
	     },
	     
	     // remove the showing image and render the pre-loaded image into the shown views
	     replace : function(preloadedImage) {
	    	this.remove();
	    	return new this.constructor({ model : preloadedImage.model, el : preloadedImage.el }).render();
	     }, 
	     
	     events : {
	    	"mouseover": "hover",
	    	"mouseout" : "unhover",
	    	"click"    : "click"
	     },
	     
	     parentHover : function() {
	     	this.controlBar.css({
					'top':"0",
					'opacity':'1'
			});
						 
			 /*this.controlBar.css({
			 		'margin':'-0.7em 3% 0 3%'
			 });
			 */
			 
			 this.controlBar.find('span').css({
			 		'opacity':'1'
			 });
	     },
	     
	     parentUnhover : function() {
				//_.delay(function(el){
	     			this.controlBar.css({
			 			'top':'0.7em'
			 		});
			 		this.controlBar.find('span').css({
			 			'opacity':'0'
			 		});
	     		//}, 800, this.controlBar);
	     		
	     },
	     
	     hover : function() {
	    	 var el = $(this.el);
	    	 
	    	 $('img.combatant').removeClass("selected notSelected");
	    	 el.addClass("selected");
	 		 var pos = el.offset();
	 		 $(el).css('cursor', function() { //------ adds magnifying glass effect
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
	     },
	     
	     unhover : function() {
	     		 
	     },
	     
	     click : function() {
	    	var el = $(this.el);
	 		var scaleFactor = 2;
			
			var documentWidth = $(window).width();
			var imgPosition = el.offset();
			var imgWidth = el.width();
			var imgWidthScaled = el.width() * scaleFactor;
			var translateOffset = (documentWidth/2) - (imgPosition.left) - (imgWidth/2);
			var zoomedOffset = documentWidth - imgWidthScaled - (imgWidth) + (imgWidthScaled / 20);

			if(currentZoomedImage.isZoomed()) {
				currentZoomedImage.reset();
				$("div#content").css("opacity",1);
				$("div#commandCenter").css("opacity",1);
				$("div#titles").css("opacity",1);
			
				$("div#zoomedImage").fadeOut(175);
				
				$("div#zoomTitleBlock").css("top",-100);
			} else {
				// if there is a zoomed image then don't try to zoom in
				if(! currentZoomedImage.canZoom(this)) return;
				currentZoomedImage.set(this);
				
				$("div#content").css("opacity",0.1);
				$("div#commandCenter").css("opacity",0.1);
				$("div#titles").css("opacity",0.1);

				$("img#zoomed").attr("src", this.model.get("src"));
				$("div#zoomedImage").fadeIn(300);
				
				this.zoomedTitle.text(this.model.get("title"));
				this.zoomedPermalink.text(this.model.get("permalink"));
				this.zoomedPermalink.attr('href',this.model.get("permalink"));
				$("div#zoomTitleBlock").each(function(i,el){//Make font as big as possible
					$(el).textfill({ maxFontPixels: 34 })
				}); 
				
				$("div#zoomInPicture img").css('cursor', function() { //------ adds magnifying glass effect
					if (jQuery.browser.mozilla) {
						return '-moz-zoom-out';
					} else if (jQuery.browser.webkit) {
						return '-webkit-zoom-out';
					} else {
					   return 'pointer'; 
					}
				});
			
				$("div#zoomTitleBlock").css("top",0);
			} 
			
			$("div#zoomedImage").toggleClass("zoomedIn"); 
	     }
     });
	
     // View for the left image. This is bound to a tag that already exists
     UI.LeftImage = UI.ShowingImage.extend({
    	 className : "combatant leftCombatant",
    	 title : $("#leftTitle"),
	     voteButton : new UI.VoteButton({ el: $("#leftVoteButton") }),
	     controlBar : $("div.leftControls"),
	     wrapper : $("div.leftWrapper"),
     });
	
     // View for the right image. This is bound to a tag that already exists
     UI.RightImage = UI.ShowingImage.extend({
    	 className : "combatant rightCombatant",
    	 title : $("#rightTitle"),
	     voteButton : new UI.VoteButton({ el: $("#rightVoteButton") }),
	     controlBar : $("div.rightControls"),
	     wrapper : $("div.rightWrapper"),
     });
     
     // initialize the controller and start the history
     window.UIController = new UIController;
 	 Backbone.history.start();
     
     // Utility functions
     function async(url, get) {
     	$.ajax({
     		   type: get == null || !get ? "POST" : "GET",
     		   url: url,
     		   success: function(msg){
     		   //    globalEvents.trigger("transactionSuccess", msg);
     		   }
     	});
     }
     
     function hideControlBar(el) {
     
     }
     
     
     
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
		$("div#titles").css("opacity",1)
		$("div#zoomedImage").fadeOut("fast");
		$("div#zoomTitleBlock").css("top",-75);	
		$("div#zoomedImage").toggleClass("zoomedIn");
		
		currentZoomedImage.reset();
	});	
 });
 
 function hideImages() {
		
		$("img.combatant").css("opacity",0);
		$("div.voteButton").css("opacity",0);
		$("div#titles").css("opacity",0);
		$("div.controlBar").css("opacity",0);
}
 
 function showImages(){
     	$("img.combatant").css("opacity",1);
     	$("div.voteButton").css("opacity",1);
     	$("div#titles").css("opacity",1);
     	$("div.controlBar").css("opacity",1);
     }

     function skipImages() {
     	$("img.combatant").css("opacity",0);
     	$("div#titles").css("opacity",0);
     	$("div.controlBar").css("opacity",0);
     }

     function fadeTextTo(fadeTo) {
     	$("div#commandCenter").find("img").addClass("jiggle");
     	$("div#commandCenterText").find("span").css("opacity","0");
     	$("div#commandCenterText").find("span").attr("message",fadeTo);
     	window.setTimeout(stopBrainJiggle, 300);

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
     
     
	function stopBrainJiggle(){
		$("div#commandCenter").find("img").removeClass("jiggle");
		$("div#commandCenterText").find("span").text($("div#commandCenterText").find("span").attr("message"));
		$("div#commandCenterText").find("span").css("opacity","1");
	}
	
	/*function hideControlBar(el) {
		el.css({
			margin:"-0.7em 3% 0 3%",
			'opacity':'1'
		});
	}*/



