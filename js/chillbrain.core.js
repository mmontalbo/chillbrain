
/**
 *
 * 	Chillbrain core. Put the entire MVC structure in here.
 *
 */

$(function() 
  {
      window.ImageModel = Backbone.Model.extend({
	      defaults: {
		  "id" : "",
		  "title" : "...",
		  "permalink" : ""
	      }
	  });
	
      window.Feed = Backbone.Collection.extend({
		
	      _.bindAll(this);

	      model: ImageModel,
	      
	      defaults: {
		  "size" : 20,
	      }

	      intialize : function() {
		  // set bindings
		  this.bind("vote",nextImages);
		  this.bind("skip",nextImages);
		  
		  // get intial images for feed
		  this.fetchMoreImages(this.get("size"));
	      },

	      // point to custom feed url
	      url: function() {
		  return this.document.url() + '/feed?n=' + this.fetchSize;
	      },

	      // triggered on a vote or skip event, returns two Images to be displayed
	      nextImages : function() {		  
		  var nextImages = _.first(this.models,2);
		  this.remove(nextImages);

		  if(this.length <= this.get("size")/2)
		      this.fetchMoreImages(this.get("size")/2);

		  this.trigger("next",nextImages);
	      },

	      // fetch n more images from the server and add them to the collection
	      fetchMoreImages : function(n) {		  
		  this.fetchSize = this.get("size") - this.length;
		  this.fetchSize = (this.fetchSize > 0) ? this.fetchSize : 0;
		  this.fetch();
	      },
	  });	

      var UI = Backbone.Controller.extend({
	
	      // the different controller mappings live here
	      routes : {
		  "imageTransition" : "transition",
		  "first"			  : "learningOne",
		  "second"		  : "learningTwo",
		  "third"			  : "learningThree",
			
	      },
		
	      transition : function() {
			
	      },
		
	      learningOne : function() {
			
	      },
		
	      learningTwo : function() {
			
	      },
		
	      learningThree : function() {
			
	      }
		
	  });
	
      UI.VoteButton = Backbone.View.extend({
	      img : null,
	      bind : function(img) {
		  this.img = img;
	      },
		
	      events : {
		  "click" : "clickButton",
	      },
		
	      clickButton : function() {
		  alert($(this.img.el).attr("src"));
	      }
		
	  });
	
      UI.Image = Backbone.View.extend({
	
	      // STUB TO TEST JSON BEING PASSED DURING RENDERING
	      modelStub : { src : "http://www.chillbrain.com/img?i=d0b4833fcd3db7f32356ae56fd73355a0c7a984f", title : "Ze Title" },
		
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

