using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace 第一题
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void vScrollBar1_Scroll(object sender, ScrollEventArgs e)
        {
            vScrollBar1.Maximum = 100; vScrollBar1.Minimum = 0;
            vScrollBar2.Maximum = 100; vScrollBar2.Minimum = 0;


        }

        private void vScrollBar1_Scroll_1(object sender, ScrollEventArgs e)
        {
            textBox1.Text = vScrollBar1.Value.ToString("d");
            vScrollBar2.Value = (vScrollBar1.Value + 3) * 2/3;
            textBox2.Text = ((vScrollBar1.Value + 3) * 2 / 3).ToString(); 

        }

        private void vScrollBar2_Scroll(object sender, ScrollEventArgs e)
        {
            textBox2.Text = vScrollBar2.Value.ToString("d");
            vScrollBar1.Value = (vScrollBar2.Value + 3) /3/2;
            textBox1.Text =( (vScrollBar2.Value + 3) /2).ToString(); 
            
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (Convert.ToInt16(textBox1.Text) >= 0 && Convert.ToInt16(textBox1.Text) <= 100)
            {
                vScrollBar1.Value = Convert.ToInt16(textBox1.Text);
                vScrollBar2.Value = (vScrollBar1.Value +3) *2/3;
                textBox2.Text = ((vScrollBar1.Value + 3) * 2 / 3).ToString();
 
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (Convert.ToInt16(textBox2.Text) >= 0 && Convert.ToInt16(textBox2.Text) <= 100)
            {
                vScrollBar2.Value = Convert.ToInt16(textBox2.Text);
                vScrollBar1.Value = (vScrollBar2.Value + 3) /3/2;
                textBox2.Text = ((vScrollBar1.Value + 3) / 2 / 3).ToString();

                

            }

        }
    }
}
