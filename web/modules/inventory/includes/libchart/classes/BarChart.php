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
	* Base bar chart class (horizontal or vertical)
	*
	* @author   Jean-Marc Trémeaux (jm.tremeaux at gmail.com)
	* @abstract
	*/

	class BarChart extends Chart
	{
		/**
		* Creates a new bar chart
		*
		* @access	protected
    		* @param	integer		width of the image
    		* @param	integer		height of the image
		*/
		
		function BarChart($width, $height)
		{
			parent::Chart($width, $height);

			$this->setMargin(5);
		}

		/**
		* Compute the boundaries on the axis
		*
		* @access	protected
		*/
		
		function computeBound()
		{
			// Compute lower and upper bound on the value axis

			$point = current($this->point);
			$yMax = $yMin = $point->getY();

			foreach($this->point as $point)
			{
				$y = $point->getY();

				if($y < $yMin)
					$yMin = $y;

				if($y > $yMax)
					$yMax = $y;
			}

			$this->yMinValue = isset($this->lowerBound) ? $this->lowerBound : $yMin;
			$this->yMaxValue = isset($this->upperBound) ? $this->upperBound : $yMax;

			// Compute boundaries on the sample axis

			$this->sampleCount = count($this->point);
		}

		/**
		* Set manually the lower boundary value (overrides the automatic formatting)
		* Typical usage is to set the bars starting from zero
		*
		* @access	public
		* @param	double		lower boundary value
		*/
		
		function setLowerBound($lowerBound)
		{
			$this->lowerBound = $lowerBound;
		}

		/**
		* Set manually the upper boundary value (overrides the automatic formatting)
		*
		* @access	public
		* @param	double		upper boundary value
		*/
		
		function setUpperBound($upperBound)
		{
			$this->upperBound = $upperBound;
		}

		/**
		* Compute the image layout
		*
		* @access	protected
		*/
		
		function computeLabelMargin()
		{
			$this->axis = new Axis($this->yMinValue, $this->yMaxValue);
			$this->axis->computeBoundaries();

			$this->graphTLX = $this->margin + $this->labelMarginLeft;
			$this->graphTLY = $this->margin + $this->labelMarginTop;
			$this->graphBRX = $this->width - $this->margin - $this->labelMarginRight;
			$this->graphBRY = $this->height - $this->margin - $this->labelMarginBottom;

		}

		/**
		* Create the image
		*
		* @access	protected
		*/
		
		function createImage()
		{
			parent::createImage();

			$this->axisColor1 = imagecolorallocate($this->img, 201, 201, 201);
			$this->axisColor2 = imagecolorallocate($this->img, 158, 158, 158);

			$this->aquaColor1 = imagecolorallocate($this->img, 242, 242, 242);
			$this->aquaColor2 = imagecolorallocate($this->img, 231, 231, 231);
			$this->aquaColor3 = imagecolorallocate($this->img, 239, 239, 239);
			$this->aquaColor4 = imagecolorallocate($this->img, 253, 253, 253);

			$this->barColor1 = imagecolorallocate($this->img, 42, 71, 181);
			$this->barColor2 = imagecolorallocate($this->img, 33, 56, 143);

			// Aqua-like background

			$aquaColor = Array($this->aquaColor1, $this->aquaColor2, $this->aquaColor3, $this->aquaColor4);

			for($i = $this->graphTLY; $i < $this->graphBRY; $i++)
				imageline($this->img, $this->graphTLX, $i, $this->graphBRX, $i, $aquaColor[($i + 3) % 4]);

			// Axis

			imagerectangle($this->img, $this->graphTLX - 1, $this->graphTLY, $this->graphTLX, $this->graphBRY, $this->axisColor1);
			imagerectangle($this->img, $this->graphTLX - 1, $this->graphBRY, $this->graphBRX, $this->graphBRY + 1, $this->axisColor1);
		}
	}
?>