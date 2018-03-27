using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data.SqlClient;
using System.Data;

public partial class zhuce : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {

    }
    protected void Button1_Click(object sender, EventArgs e)
    {
        string zhanghao = TextBox1.Text.Trim();
        string  mima= TextBox2.Text.Trim();
        SqlConnection conn = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
        conn.Open();
        SqlCommand com = new SqlCommand();
        com.CommandText = "insert into yonghu values('" + zhanghao + "','" + mima + "')";
        com.Connection = conn;
        com.ExecuteNonQuery();
        com.Dispose();
        conn.Close();
    }
}