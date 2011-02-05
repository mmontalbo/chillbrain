
/**
 *
 * 	Chillbrain core. Put the entire MVC structure in here.
 *
 */

$(function() {

	var UI = new Object();
	UI.Controller = Backbone.Controller.extend({
		
		// the different controller mappings live here
		routes : {
			":img1,:img2" 		  : "transition",
			"first"			  : "learningOne",
			"second"		  : "learningTwo",
			"third"			  : "learningThree",
			
		},
		
		transition : function(img1, img2) {
			alert("transitioned one: " + img1 + "  two:" + img2);
		},
		
		learningOne : function() {
			
		},
		
		learningTwo : function() {
			
		},
		
		learningThree : function() {
			
		},
		
		vote : function(img) {
			async("/vote?img=" + img);
		},
		
		skip : function(img, img2) {
			async("/skip?img=" + img + "&img2=" + img2);
		},
		
		share : function(img) {
			async("/share?img=" + img);
		}
		
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
			controller.vote($(this.img.el).attr("hash"));
		}
		
	});
	
	UI.Image = Backbone.View.extend({
	
		// STUB TO TEST JSON BEING PASSED DURING RENDERING
		modelStub : { src : "/img?h=agllZnBzY3JhcGVyCwsSBUltYWdlGAEM", title : "Ze Title", hash : "agllZnBzY3JhcGVyCwsSBUltYWdlGAEM" },
		
		render : function() {
			// render image
			$(this.el).attr(this.modelStub);
			
			// render title 
			$(this.title).text(this.modelStub.title);
			
			return this;
		},
		
		// utility to return the element
		html : function() {
			return this.el;
		},
		
	});
	
	// View for a preloaded image. This just sets the tag name and class name to ensure the image will be created as the proper
	// tag type with the correct styling when it is rendered
	UI.PreloadedImage = UI.Image.extend({
		tagName : "img",
		className : "preloaded"
	});
	
	// View for a shown image. These have vote buttons associated with them. 
	// Note: Subclasses MUST contain a voteButton attribute or there will be bad things
	UI.ShowingImage = UI.Image.extend({
		render : function() {
			this.voteButton.bind(this);
			return new UI.Image().render.call(this);
		},
	});
	
	// View for the left image. This is bound to a tag that already exists
	UI.LeftImage = UI.ShowingImage.extend({
		el : $("#img_0"),
		title : $("#leftTitle"),
		voteButton : new UI.VoteButton({ el: $("#leftVoteButton") }),
		events : {
			// put left image events in here
		},
	});
	
	// View for the right image. This is bound to a tag that already exists
	UI.RightImage = UI.ShowingImage.extend({
		el : $("#img_1"),
		title : $("#rightTitle"),
		voteButton : new UI.VoteButton({ el: $("#rightVoteButton") }),
		events : {
			// put right image events in here
		},
	});
	
	new UI.LeftImage().render();
	new UI.RightImage().render();
});