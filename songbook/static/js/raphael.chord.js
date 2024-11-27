/*!
 * Chord 0.1.0 - Raphael plugin
 *
 * Copyright (c) 2011 Justin D'Arcangelo (http://twitter.com/justindarc)
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) license.
 */

(function(Raphael) {
  
  Raphael.chord = function(elementOrPosition, data, labelOrVariant) {
    return new Chord(elementOrPosition, data, labelOrVariant);
  };
  
  Raphael.chord.find = function(root, name, variation) {
    if (!root) {
      return undefined;
    }
    
    if (!name) {
      name = 'maj';
    }
    
    if (!variation || variation < 1) {
      variation = 1;
    }
    
    for (var i = 0; i < Raphael.chord.data.length; i++) {
      var chordObject = Raphael.chord.data[i];
      
      for (var j = 0; j < chordObject.root.length; j++) {
        if (root === chordObject.root[j]) {
          for (var k = 0; k < chordObject.types.length; k++) {
            if (name === chordObject.types[k].name) {
              if (variation > chordObject.types[k].variations.length) {
                variation = chordObject.types[k].variations.length;
              }
              
              return chordObject.types[k].variations[variation - 1];
            }
          }
        }
      }
    }
    
    return undefined;
  };
  

  
  var Chord = function(elementOrPosition, data, labelOrVariant) {
    
    if (typeof(elementOrPosition) === 'object' && elementOrPosition.x !== undefined && elementOrPosition.y !== undefined) {
      this.element = Raphael(elementOrPosition.x, elementOrPosition.y, 100, 100);
    }
    
    else {
      this.element = Raphael(elementOrPosition, 100, 100);
    }
    
    this.element.setViewBox(0, 0, 100, 100);

    this.fret = 0;
    this.frets = [];
    this.lines = {};
    
    // Validate that the data is an array containing 6 elements.
    if (typeof(data) === 'object' && data.length !== undefined && data.length === 6) {
      this.data = data;
      
      var min = 99;
      var max = 0;
      
      for (i = 0; i < 6; i++) {
        min = (this.data[i] < min && this.data[i] > 0) ? this.data[i] : min;
        max = (this.data[i] > max && this.data[i] > 0) ? this.data[i] : max;
      }
      
      if (max > 5) {
        this.fret = min;
      }
      
      var offset = (this.fret > 0) ? this.fret - 1 : 0;
      
      for (i = 0; i < 6; i++) {
        
        // Muted strings.
        if (this.data[i] === -1) {
          this.frets[i] = this.element.path('M' + (16 + (10 * i)) + ' 7L' + (24 + (10 * i)) + ' 15M' + (16 + (10 * i)) + ' 15L' + (24 + (10 * i)) + ' 7');
        }
        
        // Open strings.
        else if (this.data[i] === 0) {
          this.frets[i] = this.element.circle(20 + (10 * i), 11, 3.5);
        }
        
        // All other strings.
        else {
          this.frets[i] = this.element.circle(20 + (10 * i), 15 + (10 * (this.data[i] - offset)), 3.5).attr({
            'fill': '#000'
          });
        }
      }
      
      if (this.fret > 0) {
        this.element.text(84, 24, this.fret + 'fr');
      } else {
        this.lines.top = this.element.path('M20 18L70 18L70 20L20 20L20 18').attr({
          'fill': '#000'
        });
      }
      
      if (labelOrVariant) {
        this.label = this.element.text(45, 78, labelOrVariant);
      }
    }
    
    // Otherwise, treat the data as a chord represented as a string (e.g.: "C maj").
    else if (typeof(data) === 'string') {
      var splitData = data.split(' ');
      var variant = 1;
      
      if (typeof(labelOrVariant) === 'number') {
        variant = labelOrVariant;
      }
      
      this.element.remove();
      
      if (splitData.length > 1) {
        return new Chord(elementOrPosition, Raphael.chord.find(splitData[0], splitData[1], variant), splitData[0] + ' ' + splitData[1]);
      } else {
        return new Chord(elementOrPosition, Raphael.chord.find(data, 'maj', variant), data);
      }
    }
    
    this.lines.horizontal = [];
    this.lines.vertical = [];
    
    for (var i = 0; i < 6; i++) {
      var position = 20 + (10 * i);
      
      this.lines.horizontal.push(this.element.path('M20 ' + position + 'L70 ' + position));
      this.lines.vertical.push(this.element.path('M' + position + ' 20L' + position + ' 70'));
    }
  };
  
  Chord.prototype.remove = function () {
    this.element.remove();
  };
  
})(window.Raphael);
