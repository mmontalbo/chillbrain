
/**
 * 
 * Chillbrain core. Put the entire MVC structure in here.
 * 
 */

var delimeter = "&";
var chillbrain = {
		constants : {
	delimiter : delimeter,
	nextRoute : ":image1" + delimeter + ":image2" 
},

event : {
	fetch : "fetchComplete",
	quickFetch : "quickFetchComplete",
	transaction : "transactionSuccess",
	transactionCallback : "transactionCallback",
	vote : "vote",
	skip : "skip",
	share : "share"
}
};

var loaded = false;
var setup = window.location.hash.length ? false : true;

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
		preloadedImages : new Object(),
		index : 2,
		isFetching: false,

		initialize : function() {
		this.bind("refresh", this.initialLoad);
		_.bindAll(this,"fetchSuccess","fetchError","getNext","addPreloaded","isExhausted","intialLoad");
	},

	initialLoad : function() {
		_.each(this.models, this.addPreloaded, this);
	},

	// point to custom feed url
	url: function() {
		return '/feed?n=' + this.fetchSize;
	},

	// fetch n more images from the server and add them to the
	// collection
	fetchMoreImages : function() {
		this.isFetching = true;
		this.fetch({
			success : this.fetchSuccess,
			error : this.fetchError,
		});
	},

	fetchSuccess : function()
	{
		//var initSize = _.values(this.preloadedImages).length;
		_.each(this.models, this.addPreloaded, this);
		//if(initSize ===  _.values(this.preloadedImages).length)
		//	alert("dupes: "+initSize)
		globalEvents.trigger(chillbrain.event.fetch);
		this.isFetching = false;
		$("#loading").css("opacity","0");
	},

	fetchError : function()
	{
		this.isFetching = false;
	},

	addPreloaded : function(image) {
		//var ind = _.indexOf(_.keys(this.preloadedImages), image.get("id"));
		//var ind2 =_.indexOf(_.keys(this.preloadedImages), image.get("id"));
		//if(ind != -1)
		//	alert("dupe: "+image.get("title")+" first:"+ind+" second:"+ind2);
		this.preloadedImages[image.get("id")] = new UI.PreloadedImage({ model : image }).render();		    
	},

	getNext : function() {						
		preloadedImageValues = _.values(this.preloadedImages);

		if(!this.isFetching &&
				(preloadedImageValues.length - this.index <= this.fetchSize-1))
		{
			this.fetchMoreImages();
		}

		model = preloadedImageValues[this.index].model;

		if(!this.isExhausted())
			this.index++;

		return model;
	},

	getNextId : function() {
		return this.getNext().get("id");
	},

	getPreloaded : function(key) {
		return this.preloadedImages[key];
	},

	isExhausted : function() {
		return this.index > _.values(this.preloadedImages).length - 3;
	},

	backup : function() {
		this.index = this.index - 2;
	},
	});	

	var fetcherEvents = new Object();
	_.extend(fetcherEvents, Backbone.Events);
	var QuickFetcher = Backbone.Collection.extend({
		model: ImageModel,
		data : null,

		initialize : function() {
		_.bindAll(this, "send");
		fetcherEvents.bind(chillbrain.event.fetch, this.send);
	},

	url : function() {
		return '/data?data=' + this.data;
	},

	send : function() {
		if(this.length == 1)
			globalEvents.trigger(chillbrain.event.quickFetch, this.models[0]);
		else
			globalEvents.trigger(chillbrain.event.quickFetch, this.models[0], this.models[1]);
	},

	get : function(images) {
		this.data = $.toJSON(images);
		this.fetch({
			success: function() {
			fetcherEvents.trigger(chillbrain.event.fetch);
		}
		});
	},
	});

	var UIController = Backbone.Controller.extend({
		feed : null,
		leftImage : null,
		rightImage: null,
		transactionPerformed : false,

		initialize : function() {
		_.bindAll(this, "transactionSuccess", "transactionCallback", "setImages", "vote", "skip", "share", "preload");

		// setup global bindings for this object
		globalEvents.bind(chillbrain.event.quickFetch, this.setImages);
		globalEvents.bind(chillbrain.event.transaction, this.transactionSuccess);
		globalEvents.bind(chillbrain.event.transactionCallback, this.transactionCallback);

		globalEvents.bind(chillbrain.event.vote, this.vote);
		globalEvents.bind(chillbrain.event.skip, this.skip);
		globalEvents.bind(chillbrain.event.share, this.share);

		this.feed = new Feed;
	},

	// the different controller mappings live here
	routes : {
		"" : "root",
		":image1&:image2" : "next",
		":image" : "oneNext"    		
	},

	// Setup the page. This will get the list of images (which have been rendered into the model)
	// and bind them to the already showing images as well as pre-load the rest of the images
	setup : function() {
		if(setup) {
			var left = this.feed.getNext();
			var right = this.feed.getNext();

			this.setImages(left, right);
		} 
	},

	root : function() {
		if(!loaded) 
			return;
		else
			this.next();
	},

	oneNext : function(image) {
		new QuickFetcher().get([image]);
	},

	next : function(image1, image2) {		    	
		// if there was no transaction being performed then we going back or initializing the page
		if(!loaded) {
			new QuickFetcher().get([image1, image2]);
			return;
		} else if(! this.transactionPerformed) {
			this.feed.backup();
			if(this.feed.index == 2) {
				image1 = this.feed.at(0).get("id");
				image2 = this.feed.at(1).get("id");
			}
		}

		this.leftImage = this.leftImage.replace(this.feed.getPreloaded(image1));
		this.rightImage = this.rightImage.replace(this.feed.getPreloaded(image2));	    	
		this.transactionPerformed = false;
	},

	vote : function(img) {
		async("/vote?img=" + img);
		this.transactionSuccess();
	},

	skip : function(img, img2) {
		async("/skip?img=" + img + "&img2=" + img2);
		this.transactionSuccess();
	},

	share : function(img) {
		async("/share?img=" + img);
	},	

	setImages : function(left, right) {
		left = (left) ? left : this.feed.getNext();
		right = (right) ? right : this.feed.getNext();

		this.leftImage = new UI.LeftImage({  model: left }).render();
		this.rightImage = new UI.RightImage({  model: right }).render();

		_.delay(showImages, 100);
	},

	transactionSuccess : function() {
		this.transactionPerformed = true;
		if(!this.feed.isExhausted())
		{
			nextHash = [this.feed.getNextId(), this.feed.getNextId()].join(chillbrain.constants.delimiter);
			$("#anchor").attr("name",nextHash);
			window.location.hash = nextHash;
		}
		else
		{
			if(!this.feed.isFetching)
				this.feed.fetchMoreImages();
			$("#loading").css("opacity","1");
		}
	},

	transactionCallback : function(callback) {
		if(callback.process_response) {			
			//fb_share(callback.id, callback.img, this.feed.preloadedImages[callback.img].model.get("title"));
		} else if(callback.error){
			if(callback.error.code == 100) {
				$("span#loginButton").addClass('pulsing');
			}

			showWarning(callback.error.msg);
		}
	},
	});

	// make UI namespace for View element
	var UI = new Object();
	UI.BindableButton = Backbone.View.extend({
		img : null,
		bind : function(img) {
		this.img = img;
	},

	events : {
		"click" : "performAction",
		"mouseover" : "hover",
		"mouseout" : "unhover",
	},

	performAction : function(){},
	hover : function() {},
	unhover : function() {}
	});

	UI.VoteButton = UI.BindableButton.extend({		
		performAction : function() {
		globalEvents.trigger("vote", this.img.getId());
	},

	hover : function() {
		$(this.img.el).css("borderColor","#000000");			
	},

	unhover : function() {
		$(this.img.el).css("borderColor","#575757");
	}
	});
	
	UI.ZoomButton = UI.BindableButton.extend({		
		performAction : function() {
		this.img.zoom();
	},
	});

	UI.ShareButton = UI.BindableButton.extend({
		performAction : function() {
		globalEvents.trigger(chillbrain.event.share, this.img.getId());
	}
	});

	UI.Image = Backbone.View.extend({
		tagName : "img",
		render : function() {
		// render image
		$(this.el).attr(this.model.toJSON());
		$(this.el).removeClass().addClass(this.className);

		// render title
		$(this.title).find('span').text(this.model.get("title"));	

		sizeTitles();

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
		$(this.el).attr(this.model.toJSON());
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
		_.bindAll(this,'parentHover','parentUnhover', 'getId');

		this.wrapper.live('mouseover',this.parentHover);
		this.wrapper.live('mouseout',this.parentUnhover);

		this.voteButton.bind(this);
		this.zoomButton.bind(this);
		this.shareButton.bind(this);

		return new UI.Image().render.call(this);
	},

	// remove the showing image and render the pre-loaded image into the shown views
	replace : function(preloadedImage) {
		$(this.el).removeClass().addClass("preloaded");
		return new this.constructor({ model : preloadedImage.model, el : preloadedImage.el }).render();
	}, 

	getId : function() {
		return this.model.get("id");
	},

	events : {
		"mouseover": "hover",
		"mouseout" : "unhover",
		"click"    : "click"
	},

	parentHover : function() {
		this.controlBar.addClass('visible');						 
		this.controlBar.find('ul').addClass('visible');
	},

	parentUnhover : function() {
		this.controlBar.removeClass('visible');				
		this.controlBar.find('ul').removeClass('visible');
	},

	hover : function() {
		var el = $(this.el);	    	 
		$('img.combatant').removeClass("selected notSelected");
		el.addClass("selected");
		var pos = el.offset();
		el.css('borderColor','black');
		this.voteButton.el.addClass("selected");
	},

	unhover : function() {
		var el = $(this.el);
		el.removeClass("selected");
		el.css('borderColor','#575757');
		this.voteButton.el.removeClass("selected");
	},

	zoom : function () {
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
	},

	click : function() {		
		globalEvents.trigger("vote", this.getId());
	}
	});

	// View for the left image. This is bound to a tag that already exists
	UI.LeftImage = UI.ShowingImage.extend({
		className : "combatant leftCombatant",
		title : $("#leftTitle"),
		voteButton : new UI.VoteButton({ el: $("#leftVoteButton") }),
		zoomButton : new UI.ZoomButton({ el: $("#leftZoom") }),
		controlBar : $("div.leftControls"),
		wrapper : $("div.leftWrapper"),
		shareButton : new UI.ShareButton({ el: $("#leftShare") }),
	});

	// View for the right image. This is bound to a tag that already exists
	UI.RightImage = UI.ShowingImage.extend({
		className : "combatant rightCombatant",
		title : $("#rightTitle"),
		voteButton : new UI.VoteButton({ el: $("#rightVoteButton") }),
		zoomButton : new UI.ZoomButton({ el: $("#rightZoom") }),
		controlBar : $("div.rightControls"),
		wrapper : $("div.rightWrapper"),
		shareButton : new UI.ShareButton({ el: $("#rightShare") }),
	});

	// initialize the controller and start the history
	window.UIController = new UIController;
	Backbone.history.start();

	// Utility functions
	function async(url, get) {
		$.ajax({
			type: get == null || !get ? "POST" : "GET",
					url: url,
					cache: false,
					success: function(msg){
			globalEvents.trigger(chillbrain.event.transactionCallback, $.parseJSON(msg));
		}
		});
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

	$("div#commandCenter").find("img").click(function(){
		$(this).addClass("jiggle");
		window.setTimeout(stopBrainJiggle, 300);
		if($("div#commandCenterText").find("span").attr("message") != "chillbrain") {
			$("div#commandCenterText").find("span").attr("message",'chillbrain');
			$("div#commandCenterText").find("span").css("opacity","0");
		}
	})

	// key bindings for page
	$(document).keyup(function(event){
		switch(event.keyCode) {
		case 32: //spacebar
			globalEvents.trigger("skip",$("img.leftCombatant").attr('id'),$("img.rightCombatant").attr('id'));
			break;
		case 37: // left arrow key
			globalEvents.trigger("vote",$("img.leftCombatant").attr('id'));
			break;
		case 39: //right arrow key
			globalEvents.trigger("vote",$("img.rightCombatant").attr('id'));
			break;
		}

		return false;
	});
		});

function hideImages() {
	$("div.wrapper").css("opacity",0);
	$("div.voteButton").css("opacity",0);
	$("div#titles").css("opacity",0);
}

function showImages(){
	$("div.wrapper").css("opacity",1);
	$("div.voteButton").css("opacity",1);
	$("div#titles").css("opacity",1);
}

function skipImages() {
	$("div.wrapper").css("opacity",0);
	$("div#titles").css("opacity",0);
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
	$("div#commandCenterText").find("span").html($("div#commandCenterText").find("span").attr("message"));
	$("div#commandCenterText").find("span").css("opacity","1");
}

function sizeTitles() {
	$("div.imgTitle").each(function(i,el){//Make font as big as possible
		$(el).textfill({ maxFontPixels: 38 })
	}); 
}

function showControls(el) {
	$("div.controlBar").find('li').addClass('visible');
}

function hideControls(el) {
	$("div.controlBar").find('li').removeClass('visible');
}

$(window).resize(function() {
	sizeTitles();
});

(function($) {
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

