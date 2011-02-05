
/**
 *
 * 	Chillbrain core. Put the entire MVC structure in here.
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

	      // point to custom feed url
	      url: function() {
	    	  return 'http://localhost:8080/feed?n=' + this.fetchSize;
	      },

	      // triggered on a vote or skip event, returns two Images to be displayed
	      getNextImages : function() {		
			  var nextImages = _.first(this.models,2);
			  this.remove(nextImages);
	
			  if(this.length <= this.size/2)
			      this.fetchMoreImages(this.fetchSize/2);
			  
			  return nextImages;
	      },

	      // fetch n more images from the server and add them to the collection
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
	
    	  initialize : function() {
    	  	  this.feed = new Feed();
    	  	  var ref = this;
    	  	  this.feed.fetchImagesWithCallback(20, {
    	  		success : function() { ref.next(ref.feed.getNextImages()); },
    	  	  });
      	  },
    	  
    	  // the different controller mappings live here
	      routes : {
			  "first":		"learningOne",
			  "second": 	"learningTwo",
			  "third" : 	"learningThree",
	      },
		
	      pageInit : function() {
	    	  
	      },
		
	      learningOne : function() {
			
	      },
		
	      learningTwo : function() {
			
	      },
		
	      learningThree : function() {
			
	      },
	      
	      next : function(nextImages) {
	    	  alert(nextImages);
	    	  new UI.LeftImage({ model : nextImages[0] }).render();
	    	  new UI.RightImage({ model : nextImages[1] }).render();
	      },
		
	      vote : function(img) {
	    	  alert(img);
	    	  async("/vote?img=" + img, { callback : this.asyncCallback, ref : this });
	      },
		
	      skip : function(img, img2) {
	    	  async("/skip?img=" + img + "&img2=" + img2, { callback : this.asyncCallback, ref : this });
	      },
		
	      share : function(img) {
	    	  async("/share?img=" + img);
	      },
	      
	      asyncCallback : function() {
	    	  this.next(this.feed.getNextImages());
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
    	  
	      render : function() {
			  // render image
			  $(this.el).attr(this.model.toJSON());
				
			  // render title 
			  $(this.title).text(this.model.get("title"));	
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
 });
