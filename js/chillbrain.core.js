
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
	
	var Feed = Backbone.Collection.extend({
		model: ImageModel,
	    fetchSize : 20,
	    size : 20,
	      
	    initialize : function() {
    	  
      	},

	    // point to custom feed url
	    url: function() {
      		return 'http://localhost:8080/feed?n=' + this.fetchSize;
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
	    fetchMoreImages : function(n) {	
	    	this.fetchSize = n;
			this.fetch();
	    },
	      
	    fetchImagesWithCallback : function(n, callback) {
	    	this.fetchSize = n;
	    	this.fetch(callback);
	    },
	});	

    var UI = new Object();
    UI.Controller = Backbone.Controller.extend({
    	feed : null,
    	preloaded : new Array(),
	
    	initialize : function() {
    		_.bindAll(this, "next", "asyncCallback");
    	  
    		this.feed = new Feed();
    	  	this.feed.fetchImagesWithCallback(20, {
    	  		success : this.asyncCallback,
    	  	});
    	},
    	  
    	// the different controller mappings live here
	    routes : {
    		"first":	"learningOne",
			"second": 	"learningTwo",
			"third" : 	"learningThree",
    	},

	    learningOne : function() {
			
	    },
		
	    learningTwo : function() {
			
	    },
		
	    learningThree : function() {
			
	    },
	      
	    next : function(nextImages) {
	    	new UI.LeftImage({ model : nextImages.pop() }).render();
	    	new UI.RightImage({ model : nextImages.pop() }).render();	   
	    },
		
	    vote : function(img) {
	    	async("/vote?img=" + img, { callback : this.asyncCallback });
	    },
		
	    skip : function(img, img2) {
	    	async("/skip?img=" + img + "&img2=" + img2, { callback : this.asyncCallback });
	    },
		
	    share : function(img) {
	    	async("/share?img=" + img);
	    },
	      
	    asyncCallback : function() {
	    	this.next();
	    },	
    });
	
	var controller = new UI.Controller;
	Backbone.history.start();
	var index = 0;
	
	UI.VoteButton = Backbone.View.extend({
		img : null,
		bind : function(img) {
			this.img = img;
		},
		
		events : {
			"click" : "vote",
		},
		
		vote : function() {
			controller.vote($(this.img.el).attr("id"));
		}
	});
	
	UI.Image = Backbone.View.extend({
		tagName : "img",
	    render : function() {
			// render image
			$(this.el).attr(this.model.toJSON());
				
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
	    show : function(showingImage) {
    		new showingImage({ model : this.model });
    		this.remove();
      	}
	 });
	
     // View for a shown image. These have vote buttons associated with them.
     // Note: Subclasses MUST contain a voteButton attribute or there will be
	 // bad things
     UI.ShowingImage = UI.Image.extend({
    	 render : function() {
		 	this.voteButton.bind(this);
		  	return new UI.Image().render.call(this);
	     },
     });
	
     // View for the left image. This is bound to a tag that already exists
     UI.LeftImage = UI.ShowingImage.extend({
    	 title : $("#leftTitle"),
	     voteButton : new UI.VoteButton({ el: $("#leftVoteButton") }),
	     events : {
		 	// put left image events in here
	      },
     });
	
     // View for the right image. This is bound to a tag that already exists
     UI.RightImage = UI.ShowingImage.extend({
    	 title : $("#rightTitle"),
	     voteButton : new UI.VoteButton({ el: $("#rightVoteButton") }),
	     events : {
		 	// put right image events in here
	     },
     });
 });
