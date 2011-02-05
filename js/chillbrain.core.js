
/**
 *
 * 	Chillbrain core. Put the entire MVC structure in here.
 *
 */

$(function() 
  {
      window.Image = Backbone.Model.extend({
	      
	      initialize: function() {
		  
	      },
	      
	      // Skip this image
	      skip: function() {
		  
	      },
	      
	      // Vote for this image
	      vote: function() {

	      },
	      
	      // Share this image
	      share: function() {

	      }
		
	  });
	
      window.Feed = Backbone.Collection.extend({
		
	      // Reference to this collection's model.
	      model: Image,
		
	      // Filter down the list of all todo items that are finished.
	      vote: function() {
		  return this.filter(function(todo){ return todo.get('done'); });
	      },
		
	      // Filter down the list to only todo items that are still not finished.
	      share: function() {
		  return this.without.apply(this, this.done());
	      },
		
	      // We keep the Todos in sequential order, despite being saved by unordered
	      // GUID in the database. This generates the next order number for new items.
	      nextOrder: function() {
		  if (!this.length) return 1;
		  return this.last().get('order') + 1;
	      },
		
	      // Todos are sorted by their original insertion order.
	      comparator: function(todo) {
		  return todo.get('order');
	      }
		
	  });
	
  });