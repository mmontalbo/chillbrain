
/**
 * 
 * Chillbrain core. Put the entire MVC structure in here.
 * 
 */

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
    		_.bindAll(this, "transactionSuccess", "fetchComplete", "vote");
    	
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
    		"first" :	"learningOne",
			"second": 	"learningTwo",
			"third" : 	"learningThree",
			"next:number"  :	"next",
    	},

	    learningOne : function() {
			
	    },
		
	    learningTwo : function() {
			
	    },
		
	    learningThree : function() {
			
	    },
	    
	    fetchComplete : function() {
	    	
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
	      
	    next : function(number) {
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
	    	window.location.hash = "next" + this.index++;
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
		},
		
		vote : function() {
			globalEvents.trigger("vote", $(this.img.el).attr("id"));
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
			  
			$("#content").append(this.el);
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
     UI.ShowingImage = UI.Image.extend({
    	 render : function() {
    	 	$(this.el).removeClass("preloaded");
		 	this.voteButton.bind(this);
		  	return new UI.Image().render.call(this);
	     },
	     
	     // remove the showing image and render the pre-loaded image into the shown views
	     replace : function(preloadedImage) {
	    	this.remove();
	    	return new this.constructor({ model : preloadedImage.model, el : preloadedImage.el }).render();
	     }
     });
	
     // View for the left image. This is bound to a tag that already exists
     UI.LeftImage = UI.ShowingImage.extend({
    	 className : "combatant leftCombatant",
    	 title : $("#leftTitle"),
	     voteButton : new UI.VoteButton({ el: $("#leftVoteButton") }),
	     events : {
		 	// put left image events in here
	      },
     });
	
     // View for the right image. This is bound to a tag that already exists
     UI.RightImage = UI.ShowingImage.extend({
    	 className : "combatant rightCombatant",
    	 title : $("#rightTitle"),
	     voteButton : new UI.VoteButton({ el: $("#rightVoteButton") }),
	     events : {
		 	// put right image events in here
	     },
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
 });
