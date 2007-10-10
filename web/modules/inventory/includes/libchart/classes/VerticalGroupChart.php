<?
	/** Libchart - PHP chart library
	*	
	* Copyright (C) 2005 Jean-Marc Trémeaux (jm.tremeaux at gmail.com)
	* 	
	* This library is free software; you can redistribute it and/or
	* modify it under the terms of the GNU Lesser General Public
	* License as published by the Free Software Foundation; either
	* version 2.1 of the License, or (at your option) any later version.
	* 
	* This library is distributed in the hope that it will be useful,
	* but WITHOUT ANY WARRANTY; without even the implied warranty of
	* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
	* Lesser General Public License for more details.
	* 
	* You should have received a copy of the GNU Lesser General Public
	* License along with this library; if not, write to the Free Software
	* Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
	* 
	*/
	
	/**
	* Vertical bar chart
	*
	* @author   Jean-Marc Trémeaux (jm.tremeaux at gmail.com)
	*/

	class VerticalGroupChart extends VerticalChart
	{
		/**
		* Creates a new vertical bar chart
		*
		* @access	public
    		* @param	integer		width of the image
    		* @param	integer		height of the image
		*/
		
		function VerticalGroupChart($width = 600, $height = 250)
		{
			parent::VerticalChart($width, $height);
      $this->label = array();
		}

		/**
		* Print the bars
		*
		* @access	private
		*/

		function printBar($barColors)
		{
			reset($this->point);

			$minValue = $this->axis->getLowerBoundary();
			$maxValue = $this->axis->getUpperBoundary();
			$stepValue = $this->axis->getTics();

      $groupNum = $this->sampleCount / count($this->label);
			$columnWidth = ($this->graphBRX - $this->graphTLX) / ($this->sampleCount + $groupNum - 1);

      $currentgroup = '';
      $index = 0;
      
      $j = 0;
      $groupChange = true;
			for($i = 0; $i < $this->sampleCount; $i++)
			{
				$point = current($this->point);
				next($this->point);

        $group = $point->getX();
        if ($group != $currentgroup) {
          $index = $index+1;
          $currentgroup = $group;
          if ($index > count($barColors)) {
            $index = 0;
          }
          if ($groupChange)
            $groupChange = false;
          else
            $groupChange = true;
        }

        if ($groupChange) {
          $j++;
        }

        $x = $this->graphTLX + $j * ($this->graphBRX - $this->graphTLX) / ($this->sampleCount + $groupNum - 1);
      
				$value = $point->getY();
				
				$ymin = $this->graphBRY - ($value - $minValue) * ($this->graphBRY - $this->graphTLY) / ($maxValue - $minValue);

				$this->text->printText($this->img, $x + $columnWidth / 2, $ymin - 5, $this->textColor, number_format($value), $this->text->fontCondensed, $this->text->HORIZONTAL_CENTER_ALIGN | $this->text->VERTICAL_BOTTOM_ALIGN);

				// Vertical bar

				$x1 = $x + $columnWidth * 1 / 9;
				$x2 = $x + $columnWidth * 8 / 9;

        $color = $barColors[$index];
        $color1 = imagecolorallocate($this->img, $color[0], $color[1], $color[2]);
        $color2 = imagecolorallocate($this->img, $color[0]+9, $color[1]+9, $color[2]+9);
				imagefilledrectangle($this->img, $x1, $ymin, $x2, $this->graphBRY - 1, $color1);
        imagefilledrectangle($this->img, $x1 + 1, $ymin + 1, $x2 - 4, $this->graphBRY - 1, $color2);
        
        $groupChange = false;
        $j++;
			}
		}

    function addGroupedPoint($point)
    { 
      array_push($this->point, $point);
    }

    function checkValues()
    {
      foreach ($this->point as $point)
      {
        $value = $point->getY();
        if (strval(floatval($value)) != strval($value))
          return false;
      }
      return true;
    }

    function computeLabelNumber()
    {
      foreach ($this->point as $point)
      {
              $this->label[$point->getDate()] = $point->getGroup();
      }
      $index = 0;
      $this->groupNum = array();
      foreach ($this->label as $date => $group)
      {
        $this->groupNum[$group] = $index;
        $index++;
      }
      reset($this->point);
    }
	

   /**
    * Print legend
    *
    * @access private
    */
                        
    function printLabel()
    { 
      $i = 0;

      $this->labelTLX = 520;
      $this->labelBoxHeight = 15;
      $this->labelTLY = 40;
                                                
      $boxX1 = $this->labelTLX + $this->margin;
      $boxX2 = $boxX1 + $this->labelBoxWidth;

      foreach($this->label as $a => $b)
      { 
        $groupNum = $this->groupNum[$b];
        $legend = "($groupNum) $a";
        
        $boxY1 = $this->labelTLY + $this->margin + $i * ($this->labelBoxHeight + $this->margin);
        $boxY2 = $boxY1 + $this->labelBoxHeight;

        $this->text->printText($this->img, $boxX2 + $this->margin, $boxY1 + $this->labelBoxHeight / 2, $this->textColor, $legend, $this->text->fontCondensed, $this->text->VERTICAL_CENTER_ALIGN);

        $i++;
      }
    }
    
    function printAxis()
    {
      $minValue = $this->axis->getLowerBoundary();
      $maxValue = $this->axis->getUpperBoundary();
      $stepValue = $this->axis->getTics();

      // Vertical axis

      for($value = $minValue; $value <= $maxValue; $value += $stepValue)
      { 
        $y = $this->graphBRY - ($value - $minValue) * ($this->graphBRY - $this->graphTLY) / ($maxValue - $minValue);  
                                                                                
        imagerectangle($this->img, $this->graphTLX - 3, $y, $this->graphTLX - 2, $y + 1, $this->axisColor1);
        imagerectangle($this->img, $this->graphTLX - 1, $y, $this->graphTLX, $y + 1, $this->axisColor2);

        $this->text->printText($this->img, $this->graphTLX - 5, $y, $this->textColor, number_format($value), $this->text->fontCondensed, $this->text->HORIZONTAL_RIGHT_ALIGN | $this->text->VERTICAL_CENTER_ALIGN);
      }
      
      // Horizontal Axis

      $groupNum = $this->sampleCount / count($this->label);
      $columnWidth = ($this->graphBRX - $this->graphTLX) / ($this->sampleCount + $groupNum - 1);
      
      reset($this->point);

      $j = 0;
      for($i = 0; $i <= $this->sampleCount; $i++)
      { 
        $x = $this->graphTLX + $i * $columnWidth;

        imagerectangle($this->img, $x - 1, $this->graphBRY + 2, $x, $this->graphBRY + 3, $this->axisColor1);
        imagerectangle($this->img, $x - 1, $this->graphBRY, $x, $this->graphBRY + 1, $this->axisColor2);

        if (($i % count($this->label)) == 0 && $j != 0) {
          $j++;
        }
        
        $x = $this->graphTLX + $j * $columnWidth;
        
        if($i < $this->sampleCount)
        { 
          $point = current($this->point);
          next($this->point);
          
          $text = $point->getX() . " (".$this->groupNum[$point->getGroup()].")";
          
          $this->text->printDiagonal($this->img, $x + $columnWidth * 1 / 3, $this->graphBRY + 10, $this->textColor, $text);
        }
        $j++;
      }
    }
      
    
		/**
		* Render the chart image
		*
		* @access	public
		* @param	string		name of the file to render the image to (optional)
		*/
		
		function render($fileName = null)
		{
      reset($this->point);
      $this->computeLabelNumber();
			$this->computeBound();
			$this->computeLabelMargin();
			$this->createImage();
			$this->printLogo();
			$this->printTitle();
			$this->printAxis();

      $barColors = array(
				array(2, 78, 0),
				array(148, 170, 36),
				array(233, 191, 49),
				array(240, 127, 41),
				array(243, 63, 34),
				array(190, 71, 47),
				array(135, 81, 60),
				array(128, 78, 162),
				array(121, 75, 255),
				array(142, 165, 250),
				array(162, 254, 239),
				array(137, 240, 166),
				array(104, 221, 71),
				array(98, 174, 35),
				array(93, 129, 1)
			);


			$this->printBar($barColors);
      $this->printLabel();

			if(isset($fileName))
				imagepng($this->img, $fileName);
			else
				imagepng($this->img);
		}
	}
?>
